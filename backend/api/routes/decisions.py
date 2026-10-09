from fastapi import APIRouter, Depends

from backend.api.schemas.decisions import (
    DecisionRequest,
    DecisionResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.decision_engine import DecisionService


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


@router.post(
    "/evaluate",
    response_model=DecisionResponse,
)
def evaluate_decision(
    request: DecisionRequest,
    user: User = Depends(get_current_user),
) -> DecisionResponse:
    return DecisionService.evaluate(
        current_inventory=request.current_inventory,
        reorder_point=request.reorder_point,
        stockout_risk=request.stockout_risk,
        overstock_risk=request.overstock_risk,
        supplier_risk_level=request.supplier_risk_level,
    )