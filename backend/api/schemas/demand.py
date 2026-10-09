from typing import Optional
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class DemandCreate(BaseModel):
    product_id: str
    date: date
    quantity: float = Field(ge=0)
    revenue: float = Field(default=0.0, ge=0)


class DemandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    date: date
    quantity: float
    revenue: float
class DemandUpdate(BaseModel):
    date: Optional[date] = None
    quantity: Optional[float] = Field(default=None, ge=0)
    revenue: Optional[float] = Field(default=None, ge=0)
