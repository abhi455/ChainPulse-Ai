from pydantic import BaseModel


class AIInsightRequest(BaseModel):
    decision: dict


class AIInsightResponse(BaseModel):
    title: str
    summary: str
    recommendation: str
    confidence: float
    category: str
