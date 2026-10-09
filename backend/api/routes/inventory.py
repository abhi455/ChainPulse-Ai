from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.inventory import (
    InventoryRequest,
    InventoryResponse as InventoryAnalysisResponse,
)
from backend.api.schemas.inventory_records import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import Product, User
from backend.inventory import InventoryService
from backend.services.inventory_record_service import InventoryRecordService


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "/analyze",
    response_model=InventoryAnalysisResponse,
)
def analyze_inventory(
    request: InventoryRequest,
    user: User = Depends(get_current_user),
) -> InventoryAnalysisResponse:
    return InventoryService.calculate(
        average_daily_demand=request.average_daily_demand,
        demand_std=request.demand_std,
        lead_time_days=request.lead_time_days,
        current_inventory=request.current_inventory,
        annual_demand=request.annual_demand,
        ordering_cost=request.ordering_cost,
        holding_cost=request.holding_cost,
        service_level_z=request.service_level_z,
    )


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory_record(
    payload: InventoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> InventoryResponse:

    product = db.get(Product, payload.product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    if product.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this product.",
        )

    try:
        record = InventoryRecordService(db).create(
            product=product,
            record_date=payload.date,
            on_hand=payload.on_hand,
            reserved=payload.reserved,
            safety_stock=payload.safety_stock,
            reorder_point=payload.reorder_point,
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
    response_model=list[InventoryResponse],
)
def list_inventory_records(
    product_id: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[InventoryResponse]:

    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
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

    records = InventoryRecordService(db).repository.get_for_product(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
    )

    return records

@router.patch(
    "/record/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory_record(
    inventory_id: str,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> InventoryResponse:
    service = InventoryRecordService(db)

    record = service.repository.get_by_id_for_organization(
        inventory_id,
        user.organization_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found.",
        )

    try:
        record = service.update(
            record,
            record_date=payload.date,
            on_hand=payload.on_hand,
            reserved=payload.reserved,
            safety_stock=payload.safety_stock,
            reorder_point=payload.reorder_point,
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
    "/record/{inventory_id}",
)
def delete_inventory_record(
    inventory_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = InventoryRecordService(db)

    record = service.repository.get_by_id_for_organization(
        inventory_id,
        user.organization_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found.",
        )

    try:
        service.repository.delete(record)
        db.commit()

        return {
            "success": True,
            "message": "Inventory record deleted.",
            "id": inventory_id,
        }

    except Exception:
        db.rollback()
        raise
