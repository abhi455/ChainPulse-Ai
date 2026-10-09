from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.intelligence.pipeline import (
    IntelligencePipelineService,
)

router = APIRouter(
    prefix="/pipeline",
    tags=["Intelligence Pipeline"],
)


@router.post("/run")
def run_pipeline(
    periods: int = 7,
    window: int = 3,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    if periods < 1 or periods > 365:
        raise HTTPException(
            status_code=422,
            detail="periods must be between 1 and 365.",
        )

    if window < 1 or window > 90:
        raise HTTPException(
            status_code=422,
            detail="window must be between 1 and 90.",
        )

    try:

        service = IntelligencePipelineService(db)

        return service.run(
            user.organization_id,
            periods,
            window,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
