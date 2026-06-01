"""Сервис-обёртка над агентом: запуск + восстановление ReAct-трейса для UI/курсовой."""
from __future__ import annotations

import time

from src.agent.agent import build_agent
from src.agent.exceptions import AgentMaxIterationsError
from src.agent.tools import make_tools
from src.db.equipment_repo import EquipmentRepository
from src.rag.config import Settings
from src.rag.pipeline import RAGPipeline


class AgentService:
    def __init__(
        self,
        pipeline: RAGPipeline,
        equipment_repo: EquipmentRepository,
        settings: Settings,
    ) -> None:
        self.settings = settings
        tools = make_tools(
            retriever=pipeline._retriever,
            equipment_repo=equipment_repo,
            top_k=settings.retrieval_top_k,
            score_threshold=settings.retrieval_score_threshold,
        )
        self._executor = build_agent(tools, settings)

    def run(self, question: str) -> dict:
        start = time.perf_counter()
        result = self._executor.invoke({"input": question})
        elapsed_ms = (time.perf_counter() - start) * 1000

        steps = result.get("intermediate_steps", [])

        # Эвристика зацикливания: достигнут лимит итераций без нормального ответа
        if len(steps) >= self.settings.agent_max_iterations:
            raise AgentMaxIterationsError(len(steps), self.settings.agent_max_iterations)

        trace: list[dict] = []
        tools_used: list[str] = []
        for action, observation in steps:
            tool_name = getattr(action, "tool", "")
            raw_input = getattr(action, "tool_input", "")
            if isinstance(raw_input, dict):
                tool_input = ", ".join(f"{k}={v}" for k, v in raw_input.items())
            else:
                tool_input = str(raw_input)
            log = str(getattr(action, "log", "") or "").strip()
            if log:
                trace.append({"type": "thought", "content": log})
            trace.append({
                "type": "action",
                "tool_name": tool_name,
                "tool_input": tool_input,
                "content": f"{tool_name}({tool_input})",
            })
            trace.append({
                "type": "observation",
                "tool_name": tool_name,
                "content": str(observation),
            })
            if tool_name and tool_name not in tools_used:
                tools_used.append(tool_name)

        answer = str(result.get("output", ""))
        trace.append({"type": "final", "content": answer})

        return {
            "answer": answer,
            "trace": trace,
            "tools_used": tools_used,
            "iterations": len(steps),
            "latency_ms": round(elapsed_ms, 2),
        }
