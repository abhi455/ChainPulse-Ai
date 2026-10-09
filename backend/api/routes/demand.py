from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.demand import DemandCreate, DemandResponse, DemandUpdate
from backend.auth.dependencies import get_current_user
from backend.database.models import Product, User
from backend.services.demand_service import DemandService


router = APIRouter(
    prefix="/demand",
    tags=["Demand"],
)


@router.post(
    "",
    response_model=DemandResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_demand(
    payload: DemandCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DemandResponse:
    product = db.get(Product, payload.product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this product.",
        )

    service = DemandService(db)

    try:
        record = service.create(
            product_id=payload.product_id,
            demand_date=payload.date,
            quantity=payload.quantity,
            revenue=payload.revenue,
        )

        db.commit()
        db.refresh(record)

        return record

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{product_id}",
    response_model=list[DemandResponse],
)
def list_demand(
    product_id: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[DemandResponse]:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this product.",
        )

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after end_date.",
        )

    return DemandService(db).list_for_product(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
    )

@router.patch(
    "/record/{demand_id}",
    response_model=DemandResponse,
)
def update_demand(
    demand_id: str,
    payload: DemandUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DemandResponse:
    service = DemandService(db)

    record = service.repository.get_by_id_for_organization(
        demand_id,
        user.organization_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand record not found.",
        )

    try:
        record = service.update(
            record,
            demand_date=payload.date,
            quantity=payload.quantity,
            revenue=payload.revenue,
        )

        db.commit()
        db.refresh(record)

        return record

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/record/{demand_id}",
)
def delete_demand(
    demand_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = DemandService(db)

    record = service.repository.get_by_id_for_organization(
        demand_id,
        user.organization_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demand record not found.",
        )

    try:
        service.repository.delete(record)
        db.commit()

        return {
            "success": True,
            "message": "Demand record deleted.",
            "id": demand_id,
        }

    except Exception:
        db.rollback()
        raise
