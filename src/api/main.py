import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent.service import AgentService
from src.api.routes.agent import router as agent_router
from src.api.routes.documents import router as documents_router
from src.api.routes.equipment import router as equipment_router
from src.api.routes.health import router as health_router
from src.api.routes.ingest import router as ingest_router
from src.api.routes.query import router as query_router
from src.db.connection import close_all_pools
from src.db.equipment_repo import EquipmentRepository
from src.rag.config import get_settings
from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    logger.info("Инициализация RAG-конвейера (pgvector)...")
    app.state.pipeline = RAGPipeline(settings)

    logger.info("Инициализация репозитория оборудования...")
    app.state.equipment_repo = EquipmentRepository(settings)

    logger.info("Инициализация LLM-агента...")
    app.state.agent_service = AgentService(
        pipeline=app.state.pipeline,
        equipment_repo=app.state.equipment_repo,
        settings=settings,
    )

    logger.info("Запуск приложения завершён")
    yield

    logger.info("Закрытие пула соединений Postgres...")
    close_all_pools()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ИСППР по техническому обслуживанию оборудования",
        description=(
            "Система поддержки принятия решений на основе LLM-агента и RAG. "
            "Агент использует поиск по нормативной документации и запросы к базе оборудования."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.allowed_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    app.include_router(health_router)
    app.include_router(ingest_router, prefix="/api/v1")
    app.include_router(query_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    app.include_router(equipment_router, prefix="/api/v1")
    app.include_router(documents_router, prefix="/api/v1")

    return app


app = create_app()
