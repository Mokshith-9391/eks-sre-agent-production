from typing import Any, Literal
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    cluster: str = Field(min_length=1, max_length=128)
    namespace: str = Field(default="default", min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=8000)

class Evidence(BaseModel):
    source: str
    summary: str
    details: dict[str, Any] = {}

class Diagnosis(BaseModel):
    incident: str
    severity: Literal["low","medium","high","critical"]
    root_cause: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = []
    recommended_actions: list[str] = []
    actions_taken: list[str] = []
    approval_required: bool = False

class GraphState(dict):
    pass
