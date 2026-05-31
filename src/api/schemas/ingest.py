from pydantic import BaseModel


class IngestResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    index_size: int
    processing_ms: float
