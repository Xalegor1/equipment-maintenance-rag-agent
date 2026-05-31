from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_with_mock_pipeline():
    mock_pipeline = MagicMock()
    mock_pipeline.ingest.return_value = {
        "doc_id": "test-uuid-1234",
        "filename": "test.pdf",
        "chunk_count": 5,
        "index_size": 5,
        "processing_ms": 200.0,
    }

    with patch("src.api.main.RAGPipeline", return_value=mock_pipeline):
        from src.api.main import create_app

        app = create_app()
        app.state.pipeline = mock_pipeline
        yield TestClient(app, raise_server_exceptions=True)


def test_health_returns_ok(client_with_mock_pipeline):
    response = client_with_mock_pipeline.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ingest_pdf_returns_200(client_with_mock_pipeline, sample_pdf_path: Path):
    with open(sample_pdf_path, "rb") as f:
        response = client_with_mock_pipeline.post(
            "/api/v1/ingest",
            files={"file": (sample_pdf_path.name, f, "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["chunk_count"] > 0
    assert "doc_id" in data
    assert "index_size" in data


def test_ingest_rejects_non_pdf(client_with_mock_pipeline):
    response = client_with_mock_pipeline.post(
        "/api/v1/ingest",
        files={"file": ("document.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400


def test_ingest_pipeline_called_once(client_with_mock_pipeline, sample_pdf_path: Path):
    with open(sample_pdf_path, "rb") as f:
        client_with_mock_pipeline.post(
            "/api/v1/ingest",
            files={"file": (sample_pdf_path.name, f, "application/pdf")},
        )
    assert client_with_mock_pipeline.app.state.pipeline.ingest.call_count == 1
