import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_pipeline
from src.api.schemas.documents import DocumentsResponse
from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


@router.get(
    "/documents",
    response_model=DocumentsResponse,
    summary="Состояние базы знаний: число документов и последние загруженные",
)
def list_documents(
    limit: int = Query(default=5, ge=1, le=50),
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> DocumentsResponse:
    try:
        return DocumentsResponse(**pipeline.list_documents(limit))
    except Exception as exc:
        logger.exception("Ошибка получения списка документов")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера") from exc
