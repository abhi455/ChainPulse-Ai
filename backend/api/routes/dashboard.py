from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.dashboard import (
    DashboardProductResponse,
    DashboardSummaryResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.dashboard import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardSummaryResponse:
    return DashboardService(db).summary(
        user.organization_id
    )


@router.get(
    "/product/{product_id}",
    response_model=DashboardProductResponse,
)
def dashboard_product(
    product_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardProductResponse:

    result = DashboardService(db).product(
        user.organization_id,
        product_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    return result
