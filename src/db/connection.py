"""Пул соединений PostgreSQL с регистрацией типа pgvector.

Один общий пул на DSN (module-level registry) — его используют и PgVectorStore
(векторное хранилище), и EquipmentRepository (база оборудования), работая с одним
инстансом Postgres. Пул создаётся лениво и закрывается на shutdown приложения.
"""
from __future__ import annotations

import threading

from pgvector.psycopg import register_vector
from psycopg import Connection
from psycopg_pool import ConnectionPool

from src.rag.config import Settings

_pools: dict[str, ConnectionPool] = {}
_lock = threading.Lock()


def _configure(conn: Connection) -> None:
    """Configure-коллбэк пула: регистрирует адаптер vector <-> list[float]."""
    register_vector(conn)


def get_pool(settings: Settings) -> ConnectionPool:
    """Вернуть (создав при необходимости) общий пул соединений для данного DSN."""
    dsn = settings.postgres_dsn
    pool = _pools.get(dsn)
    if pool is None:
        with _lock:
            pool = _pools.get(dsn)
            if pool is None:
                pool = ConnectionPool(
                    conninfo=dsn,
                    min_size=settings.postgres_pool_min_size,
                    max_size=settings.postgres_pool_max_size,
                    configure=_configure,
                    open=True,
                )
                _pools[dsn] = pool
    return pool


def close_all_pools() -> None:
    """Закрыть все открытые пулы (вызывать на shutdown приложения)."""
    with _lock:
        for pool in _pools.values():
            pool.close()
        _pools.clear()
