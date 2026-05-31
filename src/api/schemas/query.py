from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    page: int
    excerpt: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    latency_ms: float
