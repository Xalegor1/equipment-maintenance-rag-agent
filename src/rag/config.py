from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # POSTGRES_USER/PASSWORD/DB нужны образу postgres, не приложению
    )

    openai_api_key: SecretStr
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_retries: int = 3

    # PostgreSQL + pgvector
    postgres_dsn: str = "postgresql://maintenance_user:change_me@localhost:5432/maintenance_db"
    postgres_pool_min_size: int = 2
    postgres_pool_max_size: int = 5

    # RAG pipeline
    chunk_size: int = 1500
    chunk_overlap: int = 300
    retrieval_top_k: int = 6
    retrieval_score_threshold: float = 0.35

    # LLM-агент
    agent_max_iterations: int = 8
    agent_timeout_sec: float = 30.0

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:8501"

    api_url: str = "http://localhost:8000"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
