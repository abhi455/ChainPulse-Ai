from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.reports import ReportRequest
from backend.auth.dependencies import get_current_user
from backend.database.models import User
from backend.reports import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.post("/generate")
def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report_format = request.format.lower().strip()

    if report_format == "pdf":

        buffer = ReportService.generate_pdf(
            db,
            user.organization_id,
            request,
        )

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    'attachment; filename="chainpulse_report.pdf"'
            },
        )

    if report_format == "docx":

        buffer = ReportService.generate_docx(
            db,
            user.organization_id,
            request,
        )

        return StreamingResponse(
            buffer,
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            headers={
                "Content-Disposition":
                    'attachment; filename="chainpulse_report.docx"'
            },
        )

    if report_format == "xlsx":

        buffer = ReportService.generate_excel(
            db,
            user.organization_id,
            request,
        )

        return StreamingResponse(
            buffer,
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    'attachment; filename="chainpulse_report.xlsx"'
            },
        )

    raise HTTPException(
        status_code=422,
        detail="format must be pdf, docx, or xlsx",
    )
