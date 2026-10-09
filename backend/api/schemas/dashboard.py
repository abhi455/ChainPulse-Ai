from typing import Any

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    organization_id: str
    product_count: int
    active_product_count: int
    demand_record_count: int
    inventory_record_count: int
    supplier_count: int
    scenario_count: int
    simulation_run_count: int

    total_demand_quantity: float
    total_revenue: float
    average_daily_demand: float

    inventory_on_hand: float
    inventory_reserved: float
    inventory_available: float
    inventory_below_reorder: int
    inventory_stockouts: int

    average_supplier_reliability: float
    supplier_risk_level: str

    demand_risk_level: str
    inventory_risk_level: str
    overall_risk_score: float
    overall_risk_level: str
    primary_risk_drivers: list[str]

    latest_forecast_count: int
    latest_scenario_name: str | None
    latest_simulation_status: str | None

    alerts: list[str]
    recommendations: list[str]


class DashboardProductResponse(BaseModel):
    product_id: str
    sku: str
    name: str
    category: str | None
    active: bool
    lead_time_days: int

    demand_record_count: int
    total_demand_quantity: float
    total_revenue: float
    average_daily_demand: float

    latest_inventory_on_hand: float | None
    latest_inventory_reserved: float | None
    latest_safety_stock: float | None
    latest_reorder_point: float | None
    latest_stockout: bool | None

    forecast_count: int
    latest_forecast_demand: float | None
    latest_forecast_model: str | None
