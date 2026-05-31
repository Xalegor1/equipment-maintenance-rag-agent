"""Исключения агентного слоя."""


class AgentError(Exception):
    """Базовый класс ошибок агента."""


class AgentMaxIterationsError(AgentError):
    """Агент исчерпал лимит итераций ReAct-цикла, не дав финального ответа."""

    def __init__(self, iterations: int, max_iterations: int) -> None:
        self.iterations = iterations
        self.max_iterations = max_iterations
        super().__init__(
            f"Агент достиг лимита итераций ({iterations}/{max_iterations})"
        )


class AgentDatabaseError(AgentError):
    """Ошибка обращения к БД оборудования в инструменте query_equipment_db."""
