from __future__ import annotations

from backend.decision_engine import DecisionService
from backend.forecasting import ForecastService
from backend.inventory import InventoryService


class SupplyChainIntelligenceService:
    """Orchestrates forecasting, inventory optimization and decisions."""

    @staticmethod
    def analyze(
        demand: list[float],
        current_inventory: float,
        lead_time_days: float,
        annual_demand: float,
        ordering_cost: float,
        holding_cost: float,
        service_level_z: float = 1.65,
        window: int = 7,
        supplier_risk_level: str = "low",
    ) -> dict:

        if not demand:
            raise ValueError("Demand history cannot be empty.")

        if window > len(demand):
            window = len(demand)

        # 1. Forecast
        forecast = ForecastService.moving_average(
            values=demand,
            periods=1,
            window=window,
        )

        forecast_demand = forecast[0]

        # 2. Inventory optimization
        inventory = InventoryService.calculate(
            average_daily_demand=forecast_demand,
            demand_std=(
                0.0
                if len(demand) < 2
                else (
                    sum(
                        (x - (sum(demand) / len(demand))) ** 2
                        for x in demand
                    )
                    / (len(demand) - 1)
                ) ** 0.5
            ),
            lead_time_days=lead_time_days,
            current_inventory=current_inventory,
            annual_demand=annual_demand,
            ordering_cost=ordering_cost,
            holding_cost=holding_cost,
            service_level_z=service_level_z,
        )

        # 3. Decision engine
        decision = DecisionService.evaluate(
            current_inventory=current_inventory,
            reorder_point=inventory["reorder_point"],
            stockout_risk=inventory["stockout_risk"],
            overstock_risk=inventory["overstock_risk"],
            supplier_risk_level=supplier_risk_level,
        )

        return {
            "forecast": {
                "method": "moving_average",
                "next_period_demand": forecast_demand,
            },
            "inventory": inventory,
            "decision": decision,
        }
