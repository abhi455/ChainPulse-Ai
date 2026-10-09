from fastapi import APIRouter, Depends, HTTPException

from backend.api.schemas.bullwhip import (
    BullwhipRequest,
    BullwhipResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.analytics import BullwhipService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.post(
    "/bullwhip",
    response_model=BullwhipResponse,
)
def analyze_bullwhip(
    request: BullwhipRequest,
    user: User = Depends(get_current_user),
):
    try:
        return BullwhipService.evaluate(
            customer_demand=request.customer_demand,
            retailer_orders=request.retailer_orders,
            distributor_orders=request.distributor_orders,
            manufacturer_orders=request.manufacturer_orders,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
