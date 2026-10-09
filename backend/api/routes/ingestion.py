from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.auto_mapping import AutoMappingRequest
from backend.api.schemas.ingestion import (
    ImportRequest,
    ImportResponse,
    MappingRequest,
    PreviewImportRequest,
    ValidationRequest,
)
from backend.auth.dependencies import get_current_user
from backend.connectors import ConnectorRegistry
from backend.database.models import User
from backend.ingestion import IngestionService
from backend.ingestion.entity_import import EntityImportService
from backend.data_pipeline import AutoMapper


def _json_safe(value):
    """
    Convert pandas/numpy NaN/NaT values into JSON-safe None.

    FastAPI/Starlette JSON serialization rejects non-standard
    floating-point values such as NaN and Infinity.
    """
    import math
    from datetime import date, datetime

    if value is None:
        return None

    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _json_safe(item)
            for item in value
        ]

    try:
        import numpy as np

        if isinstance(value, np.generic):
            converted = value.item()

            if isinstance(converted, float):
                if not math.isfinite(converted):
                    return None

            return _json_safe(converted)
    except ImportError:
        pass

    try:
        import pandas as pd

        if pd.isna(value):
            return None
    except (ImportError, TypeError, ValueError):
        pass

    return value


router = APIRouter(
    prefix="/ingestion",
    tags=["Data Ingestion"],
)


@router.post(
    "/preview",
)
def preview(
    request: PreviewImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Return a raw preview of a connected source.

    POST preview intentionally uses the same
    DataConnectionService.preview() implementation as the
    proven GET connection preview endpoint.
    """

    service = IngestionService(db)

    try:
        result = service.connections.preview(
            user.organization_id,
            request.connection_id,
            request.limit,
        )

        return {
            "connection_id": request.connection_id,
            "columns": _json_safe(result.columns),
            "rows": _json_safe(result.rows),
            "total_rows": _json_safe(result.total_rows),
            "metadata": _json_safe(result.metadata),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
@router.post("/auto-map")
def auto_map(
    request: AutoMappingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = IngestionService(db)

    connection = service.connections.get(
        user.organization_id,
        request.connection_id,
    )

    if connection is None:
        raise HTTPException(
            status_code=404,
            detail="Data connection not found.",
        )

    try:
        import backend.connectors.bootstrap

        connector = ConnectorRegistry.create(
            connection.connector_type,
            connection.config,
        )

        preview = connector.preview(
            request.limit
        )

        return AutoMapper.suggest(
            columns=preview.columns,
            target=request.target,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/mapped-preview")
def mapped_preview(
    request: MappingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        rows = IngestionService(db).preview(
            user.organization_id,
            request.connection_id,
            request.mapping,
        )

        return {
            "rows": rows,
            "count": len(rows),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/validate")
def validate(
    request: ValidationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        result = IngestionService(db).validate(
            user.organization_id,
            request.connection_id,
            request.mapping,
            request.required_fields,
        )

        return {
            "valid": result.valid,
            "valid_rows": len(result.valid_rows),
            "invalid_rows": len(result.issues),
            "issues": [
                {
                    "row": issue.row,
                    "field": issue.field,
                    "message": issue.message,
                    "value": issue.value,
                }
                for issue in result.issues
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/import",
    response_model=ImportResponse,
)
def import_data(
    request: ImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = IngestionService(db)

    try:
        validation = service.validate(
            user.organization_id,
            request.connection_id,
            request.mapping,
            request.required_fields,
        )

        normalized = service.normalize(
            user.organization_id,
            request.connection_id,
            request.mapping,
        )

        importer = EntityImportService(db)

        target = request.target.lower().strip()

        if target == "products":
            product_rows = [
                {
                    **row,
                    "sku": row.get("product_sku"),
                    "name": row.get("product_name"),
                }
                for row in normalized
            ]

            imported, errors = importer.import_products(
                user.organization_id,
                product_rows,
            )

        elif target == "demand":
            imported, errors = importer.import_demand(
                user.organization_id,
                normalized,
            )

        elif target == "inventory":
            imported, errors = importer.import_inventory(
                user.organization_id,
                normalized,
            )

        elif target == "bullwhip":
            imported, errors = importer.import_bullwhip(
                user.organization_id,
                validation.valid_rows,
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Unsupported import target. "
                   "Use products, demand, inventory, or bullwhip."
                ),
            )

        db.commit()

        return {
            "success": not errors and not validation.issues,
            "target": target,
            "rows_received": len(normalized),
            "rows_imported": imported,
            "errors": [
                *[
                    {
                        "row": issue.row,
                        "field": issue.field,
                        "message": issue.message,
                        "value": issue.value,
                    }
                    for issue in validation.issues
                ],
                *errors,
            ],
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc





