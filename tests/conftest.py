from pathlib import Path

import pytest

from src.rag.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        openai_api_key="sk-test",
        postgres_dsn="postgresql://test:test@localhost:5432/test",
    )


@pytest.fixture
def sample_pdf_path() -> Path:
    base = Path(__file__).parent.parent / "data" / "eval" / "sample_docs"
    pdfs = list(base.glob("*.pdf"))
    if not pdfs:
        pytest.skip("Нет фикстур-PDF в data/eval/sample_docs/")
    return pdfs[0]
