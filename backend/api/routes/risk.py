from fastapi import APIRouter, Depends, HTTPException

from backend.api.schemas.risk import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.risk import RiskService


router = APIRouter(
    prefix="/risk",
    tags=["Risk"],
)


@router.post(
    "/analyze",
    response_model=RiskAnalysisResponse,
)
def analyze_risk(
    request: RiskAnalysisRequest,
    user: User = Depends(get_current_user),
) -> RiskAnalysisResponse:
    try:
        return RiskService.evaluate(
            components=request.components,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
