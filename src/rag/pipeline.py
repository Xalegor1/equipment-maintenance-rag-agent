import time
import uuid
from pathlib import Path

from src.rag.chunker import chunk_documents
from src.rag.config import Settings, get_settings
from src.rag.generator import Generator
from src.rag.loader import load_pdf
from src.rag.retriever import Retriever
from src.rag.vector_store import PgVectorStore, VectorStore

_MAX_CHUNKS = 2000


class RAGPipeline:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._store: VectorStore = PgVectorStore(self._settings)
        self._retriever = Retriever(self._store)
        self._generator = Generator(self._settings)

    @property
    def is_loaded(self) -> bool:
        return self._store.is_loaded

    @property
    def index_size(self) -> int:
        return self._store.index_size

    def list_documents(self, limit: int = 5) -> dict:
        return {
            "total": self._store.count_documents(),
            "chunks": self._store.index_size,
            "recent": self._store.list_documents(limit),
        }

    def ingest(self, pdf_path: Path, original_filename: str | None = None) -> dict:
        start = time.perf_counter()
        doc_id = str(uuid.uuid4())

        docs = load_pdf(pdf_path)
        if original_filename:
            for doc in docs:
                doc.metadata["source"] = original_filename
        chunks = chunk_documents(
            docs,
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )

        if len(chunks) > _MAX_CHUNKS:
            raise ValueError(
                f"Document produces too many chunks ({len(chunks)}); max {_MAX_CHUNKS}. "
                "Try a larger chunk_size or a smaller document."
            )

        self._store.add_documents(chunks, doc_id=doc_id)

        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "doc_id": doc_id,
            "filename": pdf_path.name,
            "chunk_count": len(chunks),
            "index_size": self._store.index_size,
            "processing_ms": round(elapsed_ms, 2),
        }

    def query(self, question: str, top_k: int | None = None) -> dict:
        start = time.perf_counter()

        k = top_k if top_k is not None else self._settings.retrieval_top_k
        context_docs = self._retriever.retrieve(
            question,
            k=k,
            score_threshold=self._settings.retrieval_score_threshold,
        )

        if not context_docs:
            if not self._store.is_loaded:
                answer = "Документы ещё не загружены. Загрузите PDF, чтобы начать работу."
            else:
                answer = "По вашему вопросу не найдено релевантных фрагментов. Переформулируйте запрос или загрузите больше документов."
            return {
                "answer": answer,
                "citations": [],
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        answer, citations = self._generator.generate(question, context_docs)

        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "answer": answer,
            "citations": citations,
            "latency_ms": round(elapsed_ms, 2),
        }
