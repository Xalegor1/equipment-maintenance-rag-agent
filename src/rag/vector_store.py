import hashlib
import threading
from typing import Protocol

from langchain_core.documents import Document

from src.db.connection import get_pool
from src.rag.config import Settings
from src.rag.embedder import EmbeddingModel

_EMBEDDING_DIMS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

# Гибридный поиск (dense + лексический FTS) с фьюзингом по Reciprocal Rank Fusion.
_HYBRID_POOL = 40  # сколько кандидатов берём из каждой ветки до фьюзинга
_RRF_K = 60        # сглаживающая константа RRF (стандартное значение)


class VectorStore(Protocol):
    @property
    def is_loaded(self) -> bool: ...
    @property
    def index_size(self) -> int: ...
    def add_documents(self, chunks: list[Document], doc_id: str | None = None) -> None: ...
    def similarity_search_with_score(self, query: str, k: int = 4) -> list[tuple[Document, float]]: ...
    def count_documents(self) -> int: ...
    def list_documents(self, limit: int = 5) -> list[dict]: ...


class PgVectorStore:
    """Векторное хранилище документации на PostgreSQL + pgvector.

    Реализует тот же протокол VectorStore, что и облачный аналог: SHA256-идентификаторы
    чанков, метаданные source/page/text, косинусный поиск (оператор <=>). Порог отсечения
    по score применяется выше — в Retriever (шкала косинуса сохраняется, 0..1).
    """

    def __init__(self, settings: Settings) -> None:
        self._expected_dim = _EMBEDDING_DIMS.get(settings.openai_embedding_model, 1536)
        self._embedder = EmbeddingModel.get_instance(settings)
        self._pool = get_pool(settings)
        self._lock = threading.Lock()
        self._cached_index_size: int = self._count()
        self._is_ready: bool = self._cached_index_size > 0

    def _count(self) -> int:
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks")
                row = cur.fetchone()
        return int(row[0]) if row else 0

    @property
    def is_loaded(self) -> bool:
        return self._is_ready

    @staticmethod
    def _vec_literal(vector: list[float]) -> str:
        # pgvector принимает текстовый литерал вида "[0.1,0.2,...]" с явным ::vector
        return "[" + ",".join(map(str, vector)) + "]"

    def add_documents(self, chunks: list[Document], doc_id: str | None = None) -> None:
        texts = [c.page_content for c in chunks]
        vectors_data = self._embedder.embed_documents(texts)

        rows = [
            (
                hashlib.sha256(
                    f"{doc_id or ''}::{chunk.metadata.get('source', '')}::{i}".encode(),
                    usedforsecurity=False,
                ).hexdigest()[:32],
                doc_id or "",
                chunk.metadata.get("source", ""),
                int(chunk.metadata.get("page", 0)),
                # PostgreSQL text не допускает NUL-байты (встречаются в тексте PDF)
                chunk.page_content.replace("\x00", ""),
                self._vec_literal(vector),
            )
            for i, (chunk, vector) in enumerate(zip(chunks, vectors_data))
        ]

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO document_chunks (id, doc_id, source, page, text, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (id) DO UPDATE
                        SET text = EXCLUDED.text,
                            embedding = EXCLUDED.embedding,
                            source = EXCLUDED.source,
                            page = EXCLUDED.page,
                            doc_id = EXCLUDED.doc_id
                    """,
                    rows,
                )
            conn.commit()

        with self._lock:
            self._cached_index_size = self._count()
        self._is_ready = True

    def similarity_search_with_score(
        self, query: str, k: int = 4
    ) -> list[tuple[Document, float]]:
        """Гибридный поиск: dense (pgvector) + лексический (русский FTS), фьюзинг по RRF.

        Порядок результатов — по RRF (лексический сигнал «спасает» куски, которые векторный
        поиск размывает из-за шумных слов в запросе). В score возвращаем косинусную близость
        (для порога в Retriever и отображения «релевантность %» во фронтенде).
        """
        query_vector = self._vec_literal(self._embedder.embed_query(query))

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH q AS (
                        SELECT %(qvec)s::vector AS qv,
                               -- OR по леммам запроса: любой совпавший термин даёт вклад,
                               -- ts_rank_cd вознаграждает частоту/полноту совпадений.
                               -- (AND-семантика websearch_to_tsquery отсекала бы куски,
                               --  где нет шумных слов вроде «масляный/силовой».)
                               to_tsquery('russian', array_to_string(
                                   tsvector_to_array(to_tsvector('russian', %(qtext)s)), ' | '
                               )) AS tsq
                    ),
                    semantic AS (
                        SELECT dc.id, ROW_NUMBER() OVER (ORDER BY dc.embedding <=> q.qv) AS rnk
                        FROM document_chunks dc, q
                        ORDER BY dc.embedding <=> q.qv
                        LIMIT %(pool)s
                    ),
                    lexical AS (
                        SELECT dc.id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(dc.tsv, q.tsq) DESC) AS rnk
                        FROM document_chunks dc, q
                        WHERE q.tsq IS NOT NULL AND dc.tsv @@ q.tsq
                        ORDER BY ts_rank_cd(dc.tsv, q.tsq) DESC
                        LIMIT %(pool)s
                    ),
                    fused AS (
                        SELECT COALESCE(s.id, l.id) AS id,
                               COALESCE(1.0 / (%(rrfk)s + s.rnk), 0)
                             + COALESCE(1.0 / (%(rrfk)s + l.rnk), 0) AS rrf
                        FROM semantic s
                        FULL OUTER JOIN lexical l ON s.id = l.id
                    )
                    SELECT dc.text, dc.source, dc.page,
                           (1 - (dc.embedding <=> q.qv)) AS score
                    FROM fused f
                    JOIN document_chunks dc ON dc.id = f.id, q
                    ORDER BY f.rrf DESC
                    LIMIT %(topk)s
                    """,
                    {
                        "qvec": query_vector,
                        "qtext": query,
                        "pool": _HYBRID_POOL,
                        "rrfk": _RRF_K,
                        "topk": k,
                    },
                )
                results = cur.fetchall()

        output: list[tuple[Document, float]] = []
        for text, source, page, score in results:
            score = float(score) if score is not None else 0.0
            doc = Document(
                page_content=text or "",
                metadata={"source": source or "", "page": page or 0, "score": score},
            )
            output.append((doc, score))
        return output

    def clear_namespace(self) -> None:
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE document_chunks")
            conn.commit()
        with self._lock:
            self._cached_index_size = 0
        self._is_ready = False

    @property
    def index_size(self) -> int:
        return self._cached_index_size

    def count_documents(self) -> int:
        """Число уникальных загруженных документов (по doc_id)."""
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(DISTINCT doc_id) FROM document_chunks")
                row = cur.fetchone()
        return int(row[0]) if row else 0

    def list_documents(self, limit: int = 5) -> list[dict]:
        """Последние загруженные документы: имя, число фрагментов, время загрузки."""
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT source, COUNT(*) AS chunk_count, MIN(created_at) AS ingested_at
                    FROM document_chunks
                    GROUP BY doc_id, source
                    ORDER BY ingested_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
        return [
            {"source": src, "chunk_count": int(cnt), "ingested_at": ts.isoformat()}
            for src, cnt, ts in rows
        ]
