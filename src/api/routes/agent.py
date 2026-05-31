import logging

from fastapi import APIRouter, Depends, HTTPException

from src.agent.exceptions import AgentDatabaseError, AgentMaxIterationsError
from src.agent.service import AgentService
from src.api.dependencies import get_agent_service
from src.api.schemas.agent import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])


@router.post(
    "/agent",
    response_model=AgentResponse,
    summary="Запрос к LLM-агенту (RAG + база оборудования)",
)
def run_agent(
    body: AgentRequest,
    agent: AgentService = Depends(get_agent_service),
) -> AgentResponse:
    try:
        result = agent.run(body.question)
        return AgentResponse(**result)
    except AgentMaxIterationsError as exc:
        logger.warning("Агент превысил лимит итераций: %s", exc)
        raise HTTPException(
            status_code=429,
            detail={"error": "max_iterations_exceeded", "message": str(exc)},
        ) from exc
    except AgentDatabaseError as exc:
        logger.error("Ошибка БД оборудования: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={"error": "database_unavailable", "message": "База оборудования временно недоступна"},
        ) from exc
    except Exception as exc:
        logger.exception("Непредвиденная ошибка агента")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера") from exc
