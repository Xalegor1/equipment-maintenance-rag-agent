from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.db.equipment_repo import Equipment


@pytest.fixture
def client_with_mock_repo():
    mock_repo = MagicMock()

    with patch("src.api.main.RAGPipeline"), \
         patch("src.api.main.EquipmentRepository", return_value=mock_repo), \
         patch("src.api.main.AgentService"):
        from src.api.main import create_app

        app = create_app()
        app.state.equipment_repo = mock_repo
        yield TestClient(app, raise_server_exceptions=True), mock_repo


def test_equipment_found_returns_200(client_with_mock_repo):
    client, repo = client_with_mock_repo
    repo.get_by_id.return_value = Equipment(
        equipment_id="ТМ-630/10-2",
        type="Трансформатор масляный 630 кВА",
        commissioned_date=date(2015, 3, 12),
        last_inspection_date=date(2024, 8, 14),
        status="в эксплуатации",
        location="ТП-1",
    )
    resp = client.get("/api/v1/equipment/ТМ-630/10-2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["equipment_id"] == "ТМ-630/10-2"
    assert data["last_inspection_date"] == "2024-08-14"


def test_equipment_not_found_returns_404(client_with_mock_repo):
    client, repo = client_with_mock_repo
    repo.get_by_id.return_value = None
    resp = client.get("/api/v1/equipment/НЕТ-ТАКОГО")
    assert resp.status_code == 404
