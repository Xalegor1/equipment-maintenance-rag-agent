from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.agent.exceptions import AgentMaxIterationsError


@pytest.fixture
def client_with_mock_agent():
    mock_agent = MagicMock()
    mock_agent.run.return_value = {
        "answer": "Рекомендация: провести внеплановый осмотр.",
        "trace": [
            {"type": "action", "tool_name": "query_equipment_db",
             "tool_input": "ТМ-630/10-2", "content": "query_equipment_db(ТМ-630/10-2)"},
            {"type": "observation", "tool_name": "query_equipment_db",
             "content": "Дата последнего осмотра: 2024-08-14"},
            {"type": "final", "content": "Рекомендация: провести внеплановый осмотр."},
        ],
        "tools_used": ["query_equipment_db"],
        "iterations": 1,
        "latency_ms": 1200.0,
    }

    with patch("src.api.main.RAGPipeline"), \
         patch("src.api.main.EquipmentRepository"), \
         patch("src.api.main.AgentService", return_value=mock_agent):
        from src.api.main import create_app

        app = create_app()
        app.state.agent_service = mock_agent
        yield TestClient(app, raise_server_exceptions=True), mock_agent


def test_agent_returns_200(client_with_mock_agent):
    client, _ = client_with_mock_agent
    resp = client.post("/api/v1/agent", json={"question": "Что делать с ТМ-630/10-2?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"].startswith("Рекомендация")
    assert data["tools_used"] == ["query_equipment_db"]
    assert any(s["type"] == "final" for s in data["trace"])


def test_agent_validation_empty_question(client_with_mock_agent):
    client, _ = client_with_mock_agent
    resp = client.post("/api/v1/agent", json={"question": ""})
    assert resp.status_code == 422


def test_agent_max_iterations_returns_429(client_with_mock_agent):
    client, mock_agent = client_with_mock_agent
    mock_agent.run.side_effect = AgentMaxIterationsError(8, 8)
    resp = client.post("/api/v1/agent", json={"question": "зацикливание"})
    assert resp.status_code == 429
