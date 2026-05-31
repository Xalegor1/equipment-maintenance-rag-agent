from datetime import date
from unittest.mock import MagicMock

import psycopg
import pytest
from langchain_core.documents import Document

from src.agent.exceptions import AgentDatabaseError
from src.agent.tools import make_tools
from src.db.equipment_repo import Equipment


def _tools(retriever=None, repo=None):
    retriever = retriever or MagicMock()
    repo = repo or MagicMock()
    tools = make_tools(retriever, repo, top_k=4, score_threshold=0.35)
    by_name = {t.name: t for t in tools}
    return by_name["search_documentation"], by_name["query_equipment_db"]


def test_search_documentation_formats_results():
    retriever = MagicMock()
    retriever.retrieve.return_value = [
        Document(page_content="Осмотр раз в месяц.", metadata={"source": "ГОСТ.pdf", "page": 6}),
    ]
    search, _ = _tools(retriever=retriever)
    out = search.func("периодичность осмотра")
    assert "ГОСТ.pdf" in out
    assert "с. 6" in out
    assert "Осмотр раз в месяц." in out


def test_search_documentation_no_results():
    retriever = MagicMock()
    retriever.retrieve.return_value = []
    search, _ = _tools(retriever=retriever)
    out = search.func("ничего")
    assert "не найдено" in out.lower()


def test_query_equipment_found():
    repo = MagicMock()
    repo.get_by_id.return_value = Equipment(
        equipment_id="ТМ-630/10-2",
        type="Трансформатор масляный",
        commissioned_date=date(2015, 3, 12),
        last_inspection_date=date(2024, 8, 14),
        status="в эксплуатации",
        location="ТП-1",
    )
    _, query_db = _tools(repo=repo)
    out = query_db.func("ТМ-630/10-2")
    assert "ТМ-630/10-2" in out
    assert "2024-08-14" in out
    assert "в эксплуатации" in out


def test_query_equipment_strips_quotes():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    _, query_db = _tools(repo=repo)
    query_db.func("'ТМ-630/10-2'")
    # кавычки сняты перед запросом в БД
    repo.get_by_id.assert_called_once_with("ТМ-630/10-2")


def test_query_equipment_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    _, query_db = _tools(repo=repo)
    out = query_db.func("НЕТ")
    assert "не найден" in out.lower()


def test_query_equipment_db_error_raises():
    repo = MagicMock()
    repo.get_by_id.side_effect = psycopg.OperationalError("connection refused")
    _, query_db = _tools(repo=repo)
    with pytest.raises(AgentDatabaseError):
        query_db.func("ТМ-630/10-2")
