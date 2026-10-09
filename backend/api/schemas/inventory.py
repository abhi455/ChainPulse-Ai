from pydantic import BaseModel, Field


class InventoryRequest(BaseModel):
    average_daily_demand: float = Field(ge=0)
    demand_std: float = Field(ge=0)
    lead_time_days: float = Field(ge=0)
    current_inventory: float = Field(ge=0)
    annual_demand: float = Field(ge=0)
    ordering_cost: float = Field(ge=0)
    holding_cost: float = Field(gt=0)
    service_level_z: float = Field(default=1.65, gt=0)


class InventoryResponse(BaseModel):
    safety_stock: float
    reorder_point: float
    economic_order_quantity: float
    days_of_inventory: float
    stockout_risk: str
    overstock_risk: str
