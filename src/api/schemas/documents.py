from pydantic import BaseModel


class DocumentInfo(BaseModel):
    source: str
    chunk_count: int
    ingested_at: str


class DocumentsResponse(BaseModel):
    total: int
    chunks: int
    recent: list[DocumentInfo]
