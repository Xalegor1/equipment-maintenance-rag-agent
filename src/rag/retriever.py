from langchain_core.documents import Document

from src.rag.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore) -> None:
        self._store = store

    def retrieve(
        self,
        query: str,
        k: int = 4,
        score_threshold: float = 0.35,
    ) -> list[Document]:
        results = self._store.similarity_search_with_score(query, k=k)

        filtered: list[Document] = []
        for doc, score in results:
            if score >= score_threshold:
                doc.metadata["score"] = round(float(score), 4)
                filtered.append(doc)

        return filtered
