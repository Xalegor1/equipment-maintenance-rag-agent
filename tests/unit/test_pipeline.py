import pathlib
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.rag.pipeline import RAGPipeline


@pytest.fixture
def pipeline_mocks():
    with patch("src.rag.pipeline.PgVectorStore") as mock_store_cls, \
         patch("src.rag.pipeline.Retriever") as mock_retriever_cls, \
         patch("src.rag.pipeline.Generator") as mock_generator_cls:

        mock_store = MagicMock()
        mock_store_cls.return_value = mock_store

        mock_retriever = MagicMock()
        mock_retriever_cls.return_value = mock_retriever

        mock_generator = MagicMock()
        mock_generator_cls.return_value = mock_generator

        settings = MagicMock()
        settings.retrieval_top_k = 4
        settings.retrieval_score_threshold = 0.35
        settings.chunk_size = 1000
        settings.chunk_overlap = 200

        pipeline = RAGPipeline(settings=settings)
        yield pipeline, mock_store, mock_retriever, mock_generator


def _doc(text: str = "content", source: str = "a.pdf", page: int = 1, score: float = 0.8) -> Document:
    return Document(page_content=text, metadata={"source": source, "page": page, "score": score})


def test_query_returns_answer_and_citations(pipeline_mocks):
    pipeline, _, mock_retriever, mock_generator = pipeline_mocks
    mock_retriever.retrieve.return_value = [_doc()]
    mock_generator.generate.return_value = (
        "Test answer.",
        [{"source": "a.pdf", "page": 1, "excerpt": "content", "score": 0.8}],
    )

    result = pipeline.query("test question")

    assert result["answer"] == "Test answer."
    assert len(result["citations"]) == 1
    assert "latency_ms" in result


def test_query_returns_no_docs_message_when_empty(pipeline_mocks):
    pipeline, mock_store, mock_retriever, mock_generator = pipeline_mocks
    mock_retriever.retrieve.return_value = []

    mock_store.is_loaded = False
    result = pipeline.query("anything")
    assert result["citations"] == []
    assert "загруж" in result["answer"].lower()
    mock_generator.generate.assert_not_called()

    mock_store.is_loaded = True
    result2 = pipeline.query("anything")
    assert result2["citations"] == []
    assert "переформул" in result2["answer"].lower()


def test_query_uses_top_k_param(pipeline_mocks):
    pipeline, _, mock_retriever, _ = pipeline_mocks
    mock_retriever.retrieve.return_value = []

    pipeline.query("question", top_k=2)

    mock_retriever.retrieve.assert_called_once_with("question", k=2, score_threshold=0.35)


def test_ingest_returns_correct_keys(pipeline_mocks):
    pipeline, mock_store, _, _ = pipeline_mocks
    mock_store.index_size = 3

    with patch("src.rag.pipeline.load_pdf") as mock_load, \
         patch("src.rag.pipeline.chunk_documents") as mock_chunk:
        mock_load.return_value = [Document(page_content="text", metadata={"source": "t.pdf"})]
        mock_chunk.return_value = [_doc("chunk1"), _doc("chunk2"), _doc("chunk3")]

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF fake")
            tmp_path = pathlib.Path(f.name)

        try:
            result = pipeline.ingest(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    assert "doc_id" in result
    assert result["chunk_count"] == 3
    assert "index_size" in result
    assert "processing_ms" in result


def test_is_loaded_delegates_to_store(pipeline_mocks):
    pipeline, mock_store, _, _ = pipeline_mocks

    mock_store.is_loaded = True
    assert pipeline.is_loaded is True

    mock_store.is_loaded = False
    assert pipeline.is_loaded is False
