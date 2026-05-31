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


class VectorStore(Protocol):
    @property
    def is_loaded(self) -> bool: ...
    @property
    def index_size(self) -> int: ...
    def add_documents(self, chunks: list[Document], doc_id: str | None = None) -> None: ...
    def similarity_search_with_score(self, query: str, k: int = 4) -> list[tuple[Document, float]]: ...


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
        query_vector = self._vec_literal(self._embedder.embed_query(query))

        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT text, source, page, (1 - (embedding <=> %s::vector)) AS score
                    FROM document_chunks
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (query_vector, query_vector, k),
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
