from langchain_openai import OpenAIEmbeddings

from src.rag.config import Settings


class EmbeddingModel:
    _instances: "dict[tuple, EmbeddingModel]" = {}

    def __init__(self, settings: Settings) -> None:
        self._embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key.get_secret_value(),
            max_retries=settings.openai_max_retries,
            timeout=30,
        )

    @classmethod
    def get_instance(cls, settings: Settings) -> "EmbeddingModel":
        key = (settings.openai_embedding_model,)
        if key not in cls._instances:
            cls._instances[key] = cls(settings)
        return cls._instances[key]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embeddings.embed_query(text)

