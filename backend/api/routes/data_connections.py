from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.data_connections import (
    DataConnectionCreate,
    DataConnectionPreviewResponse,
    DataConnectionRefreshResponse,
    DataConnectionResponse,
    DataConnectionTestResponse,
)
from backend.auth.dependencies import get_current_user
from backend.connectors import ConnectorRegistry
from backend.database.models import User
from backend.data_connections import (
    DataConnectionService,
)


router = APIRouter(
    prefix="/data-connections",
    tags=["Data Connections"],
)


@router.get(
    "/types",
)
def connection_types(
    user: User = Depends(get_current_user),
):
    return {
        "connectors": ConnectorRegistry.available()
    }


@router.get(
    "",
    response_model=list[DataConnectionResponse],
)
def list_connections(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return DataConnectionService(db).list(
        user.organization_id
    )


@router.post(
    "",
    response_model=DataConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_connection(
    request: DataConnectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    try:
        connection = DataConnectionService(
            db
        ).create(
            organization_id=user.organization_id,
            name=request.name,
            connector_type=request.connector_type,
            config=request.config,
            secrets=request.secrets,
            description=request.description,
        )

        db.commit()
        db.refresh(connection)

        return connection

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get(
    "/{connection_id}",
    response_model=DataConnectionResponse,
)
def get_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    connection = DataConnectionService(
        db
    ).get(
        user.organization_id,
        connection_id,
    )

    if connection is None:
        raise HTTPException(
            status_code=404,
            detail="Data connection not found.",
        )

    return connection


@router.post(
    "/{connection_id}/test",
    response_model=DataConnectionTestResponse,
)
def test_connection(
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
        result = service.test(
            user.organization_id,
            connection_id,
        )

        return {
            "connection_id": connection_id,
            "success": result.success,
            "message": result.message,
            "metadata": result.metadata,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{connection_id}/preview",
    response_model=DataConnectionPreviewResponse,
)
def preview_connection(
    connection_id: str,
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
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
        preview = service.preview(
            user.organization_id,
            connection_id,
            limit,
        )

        return {
            "connection_id": connection_id,
            "columns": preview.columns,
            "rows": preview.rows,
            "total_rows": preview.total_rows,
            "metadata": preview.metadata,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/{connection_id}/refresh",
    response_model=DataConnectionRefreshResponse,
)
def refresh_connection(
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
        rows = service.refresh(
            user.organization_id,
            connection_id,
        )

        return {
            "connection_id": connection_id,
            "success": True,
            "message": "Source refreshed successfully.",
            "rows": rows,
            "refreshed_at":
                connection.last_refreshed_at,
        }

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

