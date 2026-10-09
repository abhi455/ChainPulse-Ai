# pyright: reportMissingImports=false
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    title: str = Field(
        default="ChainPulse Supply Chain Report",
        min_length=1,
        max_length=200,
    )

    format: str = Field(
        default="pdf",
    )

    include_dashboard: bool = True
    include_products: bool = True
    include_risk: bool = True
    include_alerts: bool = True
    include_recommendations: bool = True
