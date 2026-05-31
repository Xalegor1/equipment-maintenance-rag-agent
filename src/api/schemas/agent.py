from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ThoughtStep(BaseModel):
    type: Literal["thought"]
    content: str


class ActionStep(BaseModel):
    type: Literal["action"]
    tool_name: str
    tool_input: str
    content: str


class ObservationStep(BaseModel):
    type: Literal["observation"]
    tool_name: str
    content: str


class FinalStep(BaseModel):
    type: Literal["final"]
    content: str


TraceStep = Annotated[
    ThoughtStep | ActionStep | ObservationStep | FinalStep,
    Field(discriminator="type"),
]


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class AgentResponse(BaseModel):
    answer: str
    trace: list[TraceStep]
    tools_used: list[str]
    iterations: int
    latency_ms: float
