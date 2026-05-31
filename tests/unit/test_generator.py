from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from pydantic import SecretStr

from src.rag.generator import Generator


@pytest.fixture
def mock_generator():
    with patch("src.rag.generator.ChatOpenAI") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "Answer based on context [source: test.pdf, page 1]."
        mock_llm_cls.return_value = mock_llm

        settings = MagicMock()
        settings.openai_chat_model = "gpt-4o-mini"
        settings.openai_api_key = SecretStr("sk-test")
        settings.openai_max_retries = 3

        gen = Generator(settings)
        yield gen, mock_llm


def _doc(text: str = "The answer is 42.", source: str = "test.pdf", page: int = 1, score: float = 0.8) -> Document:
    return Document(page_content=text, metadata={"source": source, "page": page, "score": score})


def test_generate_returns_str_answer(mock_generator):
    gen, _ = mock_generator
    answer, _ = gen.generate("What is the answer?", [_doc()])
    assert isinstance(answer, str)


def test_generate_citations_have_required_fields(mock_generator):
    gen, _ = mock_generator
    _, citations = gen.generate("question", [_doc()])
    assert len(citations) == 1
    c = citations[0]
    for field in ("source", "page", "excerpt", "score"):
        assert field in c


def test_generate_citations_source_matches_doc(mock_generator):
    gen, _ = mock_generator
    doc = _doc(source="research.pdf", page=5)
    _, citations = gen.generate("question", [doc])
    assert citations[0]["source"] == "research.pdf"
    assert citations[0]["page"] == 5


def test_best_excerpt_centers_on_keyword(mock_generator):
    gen, _ = mock_generator
    text = "Introduction. " + ("padding " * 30) + "Wasserstein distance is a metric. " + ("padding " * 30) + "End."
    result = gen._best_excerpt(text, "Wasserstein distance")
    assert "Wasserstein" in result


def test_best_excerpt_short_text_returns_unchanged(mock_generator):
    gen, _ = mock_generator
    short_text = "Short text."
    result = gen._best_excerpt(short_text, "anything", window=200)
    assert result == short_text
