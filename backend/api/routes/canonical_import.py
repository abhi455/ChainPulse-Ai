from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.data_connections import DataConnectionService
from backend.ingestion.canonical_import import (
    CanonicalImportService,
)

router = APIRouter(
    prefix="/canonical-import",
    tags=["Canonical Import"],
)


@router.get("/sheets/{connection_id}")
def sheets(
    connection_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = DataConnectionService(db)

    connection = service.get(
        user.organization_id,
        connection_id,
    )

    if connection is None:
        raise HTTPException(
            status_code=404,
            detail="Data connection not found.",
        )

    importer = CanonicalImportService(db)

    try:
        return {
            "connection_id": connection_id,
            "sheets": importer.list_sheets(
                connection.config["path"]
            ),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/import")
def import_sheet(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    connection_id = str(
        payload.get("connection_id", "")
    ).strip()

    target = str(
        payload.get("target", "")
    ).strip().lower()

    sheet_name = str(
        payload.get("sheet_name", "")
    ).strip()

    if not connection_id:
        raise HTTPException(
            status_code=422,
            detail="connection_id is required.",
        )

    if target not in {
        "suppliers",
        "products",
        "demand",
        "inventory",
    }:
        raise HTTPException(
            status_code=422,
            detail=(
                "target must be suppliers, products, "
                "demand, or inventory."
            ),
        )

    service = DataConnectionService(db)

    connection = service.get(
        user.organization_id,
        connection_id,
    )

    if connection is None:
        raise HTTPException(
            status_code=404,
            detail="Data connection not found.",
        )

    path = connection.config.get("path")

    if not path:
        raise HTTPException(
            status_code=422,
            detail="Connection has no source path.",
        )

    importer = CanonicalImportService(db)

    if not sheet_name:
        sheet_name = target

    try:

        if target == "suppliers":
            imported, errors = importer.import_suppliers(
                user.organization_id,
                path,
                sheet_name,
            )

        elif target == "products":
            imported, errors = importer.import_products(
                user.organization_id,
                path,
                sheet_name,
            )

        elif target == "demand":
            imported, errors = importer.import_demand(
                user.organization_id,
                path,
                sheet_name,
            )

        else:
            imported, errors = importer.import_inventory(
                user.organization_id,
                path,
                sheet_name,
            )

        db.commit()

        return {
            "success": len(errors) == 0,
            "connection_id": connection_id,
            "target": target,
            "sheet_name": sheet_name,
            "rows_imported": imported,
            "errors": errors,
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
