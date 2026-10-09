from pydantic import BaseModel, Field


class SupplierRequest(BaseModel):
    on_time_rate: float = Field(ge=0, le=1)
    defect_rate: float = Field(ge=0, le=1)
    actual_lead_time_days: float = Field(ge=0)
    expected_lead_time_days: float = Field(gt=0)
    supplier_cost: float = Field(ge=0)
    benchmark_cost: float = Field(gt=0)


class SupplierResponse(BaseModel):
    reliability_score: float
    quality_score: float
    lead_time_score: float
    cost_score: float
    overall_score: float
    risk_level: str
    recommendation: str
