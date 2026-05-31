from fastapi import Request

from src.agent.service import AgentService
from src.db.equipment_repo import EquipmentRepository
from src.rag.pipeline import RAGPipeline


def get_pipeline(request: Request) -> RAGPipeline:
    return request.app.state.pipeline


def get_agent_service(request: Request) -> AgentService:
    return request.app.state.agent_service


def get_equipment_repo(request: Request) -> EquipmentRepository:
    return request.app.state.equipment_repo
