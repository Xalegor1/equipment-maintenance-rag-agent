from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_with_mock_pipeline():
    mock_pipeline = MagicMock()
    mock_pipeline.query.return_value = {
        "answer": "The answer is 42.",
        "citations": [
            {"source": "doc.pdf", "page": 3, "excerpt": "...relevant text...", "score": 0.25}
        ],
        "latency_ms": 350.0,
    }

    with patch("src.api.main.RAGPipeline", return_value=mock_pipeline):
        from src.api.main import create_app

        app = create_app()
        app.state.pipeline = mock_pipeline
        yield TestClient(app, raise_server_exceptions=True)


def test_query_returns_200(client_with_mock_pipeline):
    response = client_with_mock_pipeline.post(
        "/api/v1/query",
        json={"question": "What is the answer?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "latency_ms" in data


def test_query_answer_content(client_with_mock_pipeline):
    response = client_with_mock_pipeline.post(
        "/api/v1/query",
        json={"question": "What is the answer?"},
    )
    assert response.json()["answer"] == "The answer is 42."


def test_query_citations_structure(client_with_mock_pipeline):
    response = client_with_mock_pipeline.post(
        "/api/v1/query",
        json={"question": "Anything?"},
    )
    citations = response.json()["citations"]
    assert isinstance(citations, list)
    for c in citations:
        assert "source" in c
        assert "page" in c
        assert "excerpt" in c
        assert "score" in c


def test_query_returns_200_with_empty_citations_when_no_match(client_with_mock_pipeline):
    client_with_mock_pipeline.app.state.pipeline.query.return_value = {
        "answer": "No relevant passages found for your question. Try rephrasing or uploading more documents.",
        "citations": [],
        "latency_ms": 10.0,
    }
    response = client_with_mock_pipeline.post(
        "/api/v1/query",
        json={"question": "What?"},
    )
    assert response.status_code == 200
    assert response.json()["citations"] == []


def test_query_top_k_validation(client_with_mock_pipeline):
    response = client_with_mock_pipeline.post(
        "/api/v1/query",
        json={"question": "test", "top_k": 0},
    )
    assert response.status_code == 422  # pydantic validation error
