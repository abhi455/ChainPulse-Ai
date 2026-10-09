from datetime import date

from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: str = Field(min_length=1)
    date: date
    on_hand: float = Field(ge=0)
    reserved: float = Field(default=0.0, ge=0)
    safety_stock: float = Field(default=0.0, ge=0)
    reorder_point: float = Field(default=0.0, ge=0)


class InventoryResponse(BaseModel):
    id: str
    product_id: str
    date: date
    on_hand: float
    reserved: float
    safety_stock: float
    reorder_point: float
    stockout: bool
