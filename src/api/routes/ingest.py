import logging
import os
import re
import tempfile
from pathlib import Path, PurePosixPath

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from src.api.dependencies import get_pipeline
from src.api.schemas.ingest import IngestResponse
from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)

_MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB

router = APIRouter(tags=["ingest"])


def _safe_filename(name: str) -> str:
    name = PurePosixPath(name).name
    name = re.sub(r'[^\w.\- ]', '_', name)
    return name[:100] or "document.pdf"


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile,
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    tmp_path: str | None = None
    try:
        contents = await file.read(_MAX_PDF_BYTES + 1)
        if len(contents) > _MAX_PDF_BYTES:
            raise HTTPException(status_code=413, detail="File exceeds the 20 MB limit.")
        if not contents.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Invalid PDF file.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        safe_name = _safe_filename(file.filename)
        result = await run_in_threadpool(
            pipeline.ingest, Path(tmp_path), original_filename=safe_name
        )
        result["filename"] = safe_name
        return IngestResponse(**result)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error processing ingest")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
