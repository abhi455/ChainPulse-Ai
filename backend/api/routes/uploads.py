from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from backend.auth.dependencies import get_current_user
from backend.database.models import User


router = APIRouter(
    prefix="/uploads",
    tags=["File Uploads"],
)

UPLOAD_DIR = Path("storage/uploads")
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json"}


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=(
                "Unsupported file type. "
                "Allowed: CSV, XLSX, JSON."
            ),
        )

    organization_dir = (
        UPLOAD_DIR / user.organization_id
    )
    organization_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_name = (
        f"{uuid4().hex}{extension}"
    )

    destination = (
        organization_dir / safe_name
    )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=422,
            detail="Uploaded file is empty.",
        )

    # 50 MB development limit.
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 50 MB limit.",
        )

    destination.write_bytes(contents)

    return {
        "success": True,
        "filename": file.filename,
        "stored_name": safe_name,
        "path": str(destination),
        "size_bytes": len(contents),
        "extension": extension,
        "organization_id": user.organization_id,
    }
