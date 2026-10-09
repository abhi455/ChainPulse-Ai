from pydantic import BaseModel, Field


class IntelligenceRequest(BaseModel):
    current_inventory: float = Field(ge=0)
    reorder_point: float = Field(ge=0)

    stockout_risk: str = Field(
        default="low",
        pattern="^(low|medium|high|critical)$",
    )

    overstock_risk: str = Field(
        default="low",
        pattern="^(low|medium|high|critical)$",
    )

    supplier_risk_level: str = Field(
        default="low",
        pattern="^(low|medium|high|critical)$",
    )


class IntelligenceResponse(BaseModel):
    risk_score: float
    risk_level: str
    decisions: list[dict]
