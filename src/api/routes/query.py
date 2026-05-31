import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_pipeline
from src.api.schemas.query import QueryRequest, QueryResponse
from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_documents(
    body: QueryRequest,
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> QueryResponse:
    try:
        result = pipeline.query(body.question, top_k=body.top_k)
        return QueryResponse(**result)
    except Exception as exc:
        logger.exception("Unexpected error processing query")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
