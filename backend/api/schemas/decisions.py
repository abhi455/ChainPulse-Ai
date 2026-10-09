from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    current_inventory: float = Field(ge=0)
    reorder_point: float = Field(ge=0)
    stockout_risk: str
    overstock_risk: str
    supplier_risk_level: str


class DecisionItem(BaseModel):
    action: str
    priority: str
    reason: str
    confidence: float
    category: str


class DecisionResponse(BaseModel):
    risk_score: float
    risk_level: str
    decisions: list[DecisionItem]
