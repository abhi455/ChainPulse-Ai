from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    organization_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=50)
    lead_time_days: int = Field(default=7, ge=0)
    reliability_score: float = Field(default=1.0, ge=0, le=1)


class SupplierResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    code: str
    lead_time_days: int
    reliability_score: float
    created_at: datetime
class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    reliability_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )
