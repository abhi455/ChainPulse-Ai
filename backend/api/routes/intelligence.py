from fastapi import APIRouter, Depends

from backend.api.schemas.intelligence import (
    IntelligenceRequest,
    IntelligenceResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.decision_engine import DecisionService


router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)


@router.post(
    "/analyze",
    response_model=IntelligenceResponse,
)
def analyze(
    request: IntelligenceRequest,
    user: User = Depends(get_current_user),
) -> IntelligenceResponse:
    return DecisionService.evaluate(
        current_inventory=request.current_inventory,
        reorder_point=request.reorder_point,
        stockout_risk=request.stockout_risk,
        overstock_risk=request.overstock_risk,
        supplier_risk_level=request.supplier_risk_level,
    )