from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.services import ProductService


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProductResponse:

    # Only administrators can create products.
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    # Prevent creating products for another organization.
    if payload.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization.",
        )

    service = ProductService(db)

    try:
        product = service.create(
            organization_id=user.organization_id,
            sku=payload.sku,
            name=payload.name,
            category=payload.category,
            unit_cost=payload.unit_cost,
            selling_price=payload.selling_price,
            lead_time_days=payload.lead_time_days,
        )

        db.commit()
        db.refresh(product)

        return product

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_products(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ProductResponse]:

    return ProductService(db).list(
        user.organization_id
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProductResponse:

    product = ProductService(db).get(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    # Prevent access to another organization's product.
    if product.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this product.",
        )

    return product

# CHAINPULSE_PRODUCT_CRUD

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProductResponse:

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    from backend.database.models import Product, Supplier

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

    updates = payload.model_dump(exclude_unset=True)

    if "sku" in updates:
        sku = updates["sku"].strip()

        if not sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU cannot be empty.",
            )

        duplicate = db.scalar(
            select(Product).where(
                Product.organization_id == user.organization_id,
                Product.sku == sku,
                Product.id != product_id,
            )
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SKU '{sku}' already exists in this organization.",
            )

        updates["sku"] = sku

    if "name" in updates and updates["name"] is not None:
        updates["name"] = updates["name"].strip()

        if not updates["name"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product name cannot be empty.",
            )

    if "supplier_id" in updates and updates["supplier_id"] is not None:

        supplier = db.get(Supplier, updates["supplier_id"])

        if supplier is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found.",
            )

        if supplier.organization_id != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supplier does not belong to your organization.",
            )

    for field, value in updates.items():
        setattr(product, field, value)

    try:
        db.flush()
        db.refresh(product)
        return product

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product update conflicts with existing data.",
        ) from exc


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    from backend.database.models import Product

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

    try:
        # Permanent deletion.
        #
        # Product relationships are configured with:
        #   demand_records   -> cascade="all, delete-orphan"
        #   inventory_records -> cascade="all, delete-orphan"
        #   forecasts        -> cascade="all, delete-orphan"
        #
        # SQLAlchemy therefore removes the related records together
        # with the product instead of leaving orphaned records.
        db.delete(product)
        db.commit()

        return {
            "success": True,
            "message": "Product permanently deleted.",
            "id": product_id,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product cannot be deleted because it is referenced by existing data.",
        ) from exc

