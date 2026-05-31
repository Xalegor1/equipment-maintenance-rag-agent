from datetime import date
from unittest.mock import MagicMock

from src.db.equipment_repo import Equipment, EquipmentRepository


def _make_pool(fetchone=None, fetchall=None):
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall or []
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    pool = MagicMock()
    pool.connection.return_value.__enter__.return_value = conn
    return pool


def _repo(pool):
    repo = EquipmentRepository.__new__(EquipmentRepository)
    repo._pool = pool
    return repo


def test_get_by_id_found():
    row = {
        "equipment_id": "ТМ-630/10-2",
        "type": "Трансформатор",
        "commissioned_date": date(2015, 3, 12),
        "last_inspection_date": date(2024, 8, 14),
        "status": "в эксплуатации",
        "location": "ТП-1",
    }
    repo = _repo(_make_pool(fetchone=row))
    rec = repo.get_by_id("ТМ-630/10-2")
    assert isinstance(rec, Equipment)
    assert rec.equipment_id == "ТМ-630/10-2"
    assert rec.to_dict()["last_inspection_date"] == "2024-08-14"


def test_get_by_id_not_found():
    repo = _repo(_make_pool(fetchone=None))
    assert repo.get_by_id("НЕТ-ТАКОГО") is None


def test_get_overdue_returns_list():
    rows = [
        {
            "equipment_id": "РВЗ-10/400-1",
            "type": "Разъединитель",
            "commissioned_date": date(2014, 6, 17),
            "last_inspection_date": date(2023, 12, 1),
            "status": "в эксплуатации",
            "location": "ГРУ-10 кВ",
        }
    ]
    repo = _repo(_make_pool(fetchall=rows))
    overdue = repo.get_overdue(months=12)
    assert len(overdue) == 1
    assert overdue[0].equipment_id == "РВЗ-10/400-1"
