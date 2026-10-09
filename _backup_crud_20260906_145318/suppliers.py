from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.supplier_records import (
    SupplierCreate,
    SupplierResponse,
)
from backend.api.schemas.suppliers import (
    SupplierRequest,
    SupplierResponse as SupplierEvaluationResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import Supplier, User
from backend.supplier_intelligence import SupplierService
from backend.services.supplier_record_service import SupplierRecordService


router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


@router.post(
    "/evaluate",
    response_model=SupplierEvaluationResponse,
)
def evaluate_supplier(
    request: SupplierRequest,
    user: User = Depends(get_current_user),
):
    return SupplierService.evaluate(
        on_time_rate=request.on_time_rate,
        defect_rate=request.defect_rate,
        actual_lead_time_days=request.actual_lead_time_days,
        expected_lead_time_days=request.expected_lead_time_days,
        supplier_cost=request.supplier_cost,
        benchmark_cost=request.benchmark_cost,
    )


@router.post(
    "",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SupplierResponse:

    if payload.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization.",
        )

    try:
        supplier = SupplierRecordService(db).create(
            organization_id=user.organization_id,
            name=payload.name,
            code=payload.code,
            lead_time_days=payload.lead_time_days,
            reliability_score=payload.reliability_score,
        )

        db.commit()
        db.refresh(supplier)

        return supplier

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[SupplierResponse],
)
def list_suppliers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SupplierResponse]:

    return SupplierRecordService(db).list_for_organization(
        user.organization_id
    )


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
)
def get_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SupplierResponse:

    supplier = SupplierRecordService(db).get(supplier_id)

    if supplier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found.",
        )

    if supplier.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this supplier.",
        )

    return supplier
