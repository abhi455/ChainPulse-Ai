from pydantic import BaseModel, Field


class ScenarioRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    demand_change_pct: float = Field(default=0, ge=-100)
    lead_time_change_pct: float = Field(default=0, ge=-100)
    inventory_change_pct: float = Field(default=0, ge=-100)


class SimulationRequest(BaseModel):
    scenario: ScenarioRequest
    average_daily_demand: float = Field(ge=0)
    demand_std: float = Field(ge=0)
    lead_time_days: float = Field(ge=0)
    current_inventory: float = Field(ge=0)
    annual_demand: float = Field(ge=0)
    ordering_cost: float = Field(ge=0)
    holding_cost: float = Field(gt=0)
    service_level_z: float = Field(default=1.65, gt=0)
