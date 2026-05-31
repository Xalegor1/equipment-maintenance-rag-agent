from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.agent.exceptions import AgentMaxIterationsError
from src.agent.service import AgentService


def _service(executor, max_iterations=8):
    svc = AgentService.__new__(AgentService)
    svc.settings = SimpleNamespace(agent_max_iterations=max_iterations)
    svc._executor = executor
    return svc


def _action(tool, tool_input, log=""):
    return SimpleNamespace(tool=tool, tool_input=tool_input, log=log)


def test_run_builds_trace_from_steps():
    executor = MagicMock()
    executor.invoke.return_value = {
        "output": "Рекомендация: провести осмотр.",
        "intermediate_steps": [
            (_action("query_equipment_db", "ТМ-630/10-2", "Нужно проверить БД"),
             "Дата последнего осмотра: 2024-08-14"),
            (_action("search_documentation", "периодичность осмотра"),
             "[Источник: ГОСТ.pdf, с. 6] Осмотр раз в месяц."),
        ],
    }
    svc = _service(executor)
    result = svc.run("Трансформатор ТМ-630/10-2 — что делать?")

    assert result["answer"].startswith("Рекомендация")
    assert result["iterations"] == 2
    assert result["tools_used"] == ["query_equipment_db", "search_documentation"]

    types = [s["type"] for s in result["trace"]]
    assert "action" in types and "observation" in types
    assert types[-1] == "final"
    # есть шаг-мысль (log непустой у первого действия)
    assert any(s["type"] == "thought" for s in result["trace"])


def test_run_raises_on_max_iterations():
    steps = [(_action("search_documentation", str(i)), "obs") for i in range(8)]
    executor = MagicMock()
    executor.invoke.return_value = {"output": "", "intermediate_steps": steps}
    svc = _service(executor, max_iterations=8)
    with pytest.raises(AgentMaxIterationsError):
        svc.run("зацикливание")


def test_run_dedups_tools_used():
    executor = MagicMock()
    executor.invoke.return_value = {
        "output": "ok",
        "intermediate_steps": [
            (_action("search_documentation", "a"), "o1"),
            (_action("search_documentation", "b"), "o2"),
        ],
    }
    svc = _service(executor)
    result = svc.run("вопрос")
    assert result["tools_used"] == ["search_documentation"]
