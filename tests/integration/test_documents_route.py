from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_with_mock_pipeline():
    mock_pipeline = MagicMock()
    mock_pipeline.list_documents.return_value = {
        "total": 2,
        "chunks": 938,
        "recent": [
            {"source": "РД 34.45-51.300-97.pdf", "chunk_count": 399, "ingested_at": "2026-06-01T12:00:00"},
            {"source": "ПТЭЭП.pdf", "chunk_count": 539, "ingested_at": "2026-06-01T12:10:00"},
        ],
    }

    with patch("src.api.main.RAGPipeline", return_value=mock_pipeline), \
         patch("src.api.main.EquipmentRepository"), \
         patch("src.api.main.AgentService"):
        from src.api.main import create_app

        app = create_app()
        app.state.pipeline = mock_pipeline
        yield TestClient(app, raise_server_exceptions=True)


def test_documents_returns_200(client_with_mock_pipeline):
    resp = client_with_mock_pipeline.get("/api/v1/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["chunks"] == 938
    assert len(data["recent"]) == 2
    assert data["recent"][0]["source"].startswith("РД")


def test_documents_limit_validation(client_with_mock_pipeline):
    resp = client_with_mock_pipeline.get("/api/v1/documents", params={"limit": 0})
    assert resp.status_code == 422
