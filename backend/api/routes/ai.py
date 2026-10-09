from fastapi import APIRouter, Depends

from backend.ai import InsightService
from backend.api.schemas.ai import (
    AIInsightRequest,
    AIInsightResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import User


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/explain",
    response_model=AIInsightResponse,
)
def explain_decision(
    request: AIInsightRequest,
    user: User = Depends(get_current_user),
) -> AIInsightResponse:
    insight = InsightService().explain_decision(
        request.decision
    )

    return AIInsightResponse(
        title=insight.title,
        summary=insight.summary,
        recommendation=insight.recommendation,
        confidence=insight.confidence,
        category=insight.category,
    )