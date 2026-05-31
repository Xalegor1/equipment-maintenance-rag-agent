"""Репозиторий доступа к базе оборудования (таблица equipment)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from psycopg.rows import dict_row

from src.db.connection import get_pool
from src.rag.config import Settings


@dataclass
class Equipment:
    equipment_id: str
    type: str
    commissioned_date: date
    last_inspection_date: date
    status: str
    location: str | None

    def to_dict(self) -> dict:
        return {
            "equipment_id": self.equipment_id,
            "type": self.type,
            "commissioned_date": self.commissioned_date.isoformat(),
            "last_inspection_date": self.last_inspection_date.isoformat(),
            "status": self.status,
            "location": self.location,
        }


class EquipmentRepository:
    def __init__(self, settings: Settings) -> None:
        self._pool = get_pool(settings)

    def get_by_id(self, equipment_id: str) -> Equipment | None:
        """Вернуть единицу оборудования по идентификатору или None, если не найдена."""
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT equipment_id, type, commissioned_date,
                           last_inspection_date, status, location
                    FROM equipment
                    WHERE equipment_id = %s
                    """,
                    (equipment_id,),
                )
                row = cur.fetchone()
        return Equipment(**row) if row else None

    def get_overdue(self, months: int = 12) -> list[Equipment]:
        """Оборудование, не осматривавшееся дольше указанного числа месяцев
        (исключая выведенное из эксплуатации), от самых давних к свежим."""
        with self._pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT equipment_id, type, commissioned_date,
                           last_inspection_date, status, location
                    FROM equipment
                    WHERE last_inspection_date < (CURRENT_DATE - make_interval(months => %s))
                      AND status <> 'выведено из эксплуатации'
                    ORDER BY last_inspection_date ASC
                    """,
                    (months,),
                )
                rows = cur.fetchall()
        return [Equipment(**row) for row in rows]
