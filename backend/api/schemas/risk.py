from pydantic import BaseModel, Field
from typing import Dict, List

class RiskComponentDetail(BaseModel):
    component: str
    score: float
    level: str

class RiskAnalysisRequest(BaseModel):
    components: Dict[str, str] = Field(
        ..., 
        example={"demand": "high", "inventory": "medium", "supplier": "low", "bullwhip": "critical"},
        description="Dictionary mapping risk components to their current string levels."
    )

class RiskAnalysisResponse(BaseModel):
    overall_score: float
    risk_level: str
    primary_drivers: List[str]
    component_details: List[RiskComponentDetail]
