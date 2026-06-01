"""Инструменты (tools) LLM-агента.

Фабрика make_tools инъектирует зависимости (Retriever, EquipmentRepository) через
замыкание — это даёт singleton-поведение и тестируемость без глобального состояния.
"""
from __future__ import annotations

from datetime import date

import psycopg
from langchain_core.tools import BaseTool, tool

from src.agent.exceptions import AgentDatabaseError
from src.db.equipment_repo import EquipmentRepository
from src.rag.retriever import Retriever


def make_tools(
    retriever: Retriever,
    equipment_repo: EquipmentRepository,
    top_k: int,
    score_threshold: float,
) -> list[BaseTool]:
    @tool
    def search_documentation(query: str) -> str:
        """Поиск в нормативной документации по техническому обслуживанию (ГОСТы, РД, ПТЭЭП).
        Возвращает релевантные фрагменты с указанием источника и страницы. Используй для
        поиска требований, периодичности осмотров, процедур и норм испытаний."""
        docs = retriever.retrieve(query, k=top_k, score_threshold=score_threshold)
        if not docs:
            return "По запросу не найдено релевантных фрагментов в документации."
        parts = []
        for doc in docs:
            source = doc.metadata.get("source", "неизвестно")
            page = doc.metadata.get("page", "?")
            parts.append(f"[Источник: {source}, с. {page}] {doc.page_content}")
        return "\n\n".join(parts)

    @tool
    def query_equipment_db(equipment_id: str) -> str:
        """Данные о единице оборудования по идентификатору (например 'ТМ-630/10-2'):
        тип, дата ввода в эксплуатацию, дата последнего осмотра, статус, расположение.
        Вызывай ПЕРВЫМ, если в запросе упомянут идентификатор оборудования."""
        # LLM иногда оборачивает аргумент в кавычки — снимаем их
        clean_id = equipment_id.strip().strip("'\"").strip()
        try:
            rec = equipment_repo.get_by_id(clean_id)
        except psycopg.Error as exc:  # реальная ошибка БД — пробрасываем наверх
            raise AgentDatabaseError(str(exc)) from exc

        if rec is None:
            return f"Оборудование с идентификатором '{clean_id}' не найдено в базе."

        # Считаем «возраст» последнего осмотра сами — gpt-4o-mini плохо считает даты
        days = (date.today() - rec.last_inspection_date).days
        months = days // 30
        since = f"{months} мес. ({days} дн.) назад" if days >= 0 else "дата в будущем"

        return (
            f"Идентификатор: {rec.equipment_id}\n"
            f"Тип: {rec.type}\n"
            f"Дата ввода в эксплуатацию: {rec.commissioned_date.isoformat()}\n"
            f"Дата последнего осмотра: {rec.last_inspection_date.isoformat()} "
            f"(сегодня {date.today().isoformat()}, то есть {since})\n"
            f"Статус: {rec.status}\n"
            f"Расположение: {rec.location or 'не указано'}"
        )

    return [search_documentation, query_equipment_db]
