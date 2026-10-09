from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.data_connections import DataConnectionService


router = APIRouter(
    prefix="/data-import",
    tags=["Data Import"],
)


@router.post("/upload")
async def upload_and_create_connection(
    file: UploadFile = File(...),
    name: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = "." + file.filename.lower().rsplit(".", 1)[-1]

    extension_map = {
        ".csv": "csv",
        ".xlsx": "xlsx",
        ".json": "json",
    }

    connector_type = extension_map.get(extension)

    if connector_type is None:
        raise HTTPException(
            status_code=422,
            detail="Supported files: CSV, XLSX, JSON.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=422,
            detail="Uploaded file is empty.",
        )

    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 50 MB limit.",
        )

    from pathlib import Path
    from uuid import uuid4

    upload_dir = (
        Path("storage/uploads")
        / user.organization_id
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_name = (
        f"{uuid4().hex}{extension}"
    )

    path = upload_dir / stored_name
    path.write_bytes(contents)

    connection_name = (
        name.strip()
        if name and name.strip()
        else file.filename
    )

    connection = DataConnectionService(db).create(
        organization_id=user.organization_id,
        name=connection_name,
        connector_type=connector_type,
        config={
            "path": str(path),
            "original_filename": file.filename,
        },
        description="Uploaded data source",
    )

    db.commit()
    db.refresh(connection)

    return {
        "success": True,
        "connection_id": connection.id,
        "name": connection.name,
        "connector_type": connection.connector_type,
        "filename": file.filename,
        "size_bytes": len(contents),
        "status": connection.status,
    }
