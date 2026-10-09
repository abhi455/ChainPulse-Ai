from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user
from backend.connectors import ConnectorRegistry
from backend.database.models import User
from backend.data_connections import DataConnectionService


router = APIRouter(
    prefix="/data-connections",
    tags=["Data Connections"],
)


@router.get("/{connection_id}/metadata")
def connection_metadata(
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

    try:
        import backend.connectors.bootstrap

        connector = ConnectorRegistry.create(
            connection.connector_type,
            connection.config,
        )

        result = connector.test_connection()

        metadata = result.metadata or {}

        return {
            "connection_id": connection.id,
            "connector_type": connection.connector_type,
            "status": (
                "healthy"
                if result.success
                else "error"
            ),
            "message": result.message,
            "metadata": metadata,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/{connection_id}/sheet")
def change_excel_sheet(
    connection_id: str,
    sheet: str | int,
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

    if connection.connector_type != "xlsx":
        raise HTTPException(
            status_code=422,
            detail="Sheet selection is only supported for XLSX.",
        )

    connection.config = {
        **connection.config,
        "sheet": sheet,
    }

    connection.last_tested_at = None
    connection.status = "configured"

    db.commit()
    db.refresh(connection)

    return {
        "success": True,
        "connection_id": connection.id,
        "sheet": sheet,
    }


@router.post("/{connection_id}/table")
def change_sql_table(
    connection_id: str,
    table: str,
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

    if connection.connector_type != "sql":
        raise HTTPException(
            status_code=422,
            detail="Table selection is only supported for SQL.",
        )

    if not table.strip():
        raise HTTPException(
            status_code=422,
            detail="Table name cannot be empty.",
        )

    connection.config = {
        **connection.config,
        "table": table.strip(),
    }

    # A table selection should replace query mode.
    connection.config.pop("query", None)

    connection.last_tested_at = None
    connection.status = "configured"

    db.commit()
    db.refresh(connection)

    return {
        "success": True,
        "connection_id": connection.id,
        "table": table.strip(),
    }
