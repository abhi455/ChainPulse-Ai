from backend.inventory import InventoryService
from backend.simulation.metrics import (
    impact_level,
    percentage_change,
)
from backend.simulation.models import Scenario


class SimulationService:

    @staticmethod
    def run(
        scenario: Scenario,
        average_daily_demand: float,
        demand_std: float,
        lead_time_days: float,
        current_inventory: float,
        annual_demand: float,
        ordering_cost: float,
        holding_cost: float,
        service_level_z: float = 1.65,
    ) -> dict:
        baseline = InventoryService.calculate(
            average_daily_demand=average_daily_demand,
            demand_std=demand_std,
            lead_time_days=lead_time_days,
            current_inventory=current_inventory,
            annual_demand=annual_demand,
            ordering_cost=ordering_cost,
            holding_cost=holding_cost,
            service_level_z=service_level_z,
        )

        scenario_daily_demand = Scenario.apply_percentage(
            average_daily_demand,
            scenario.demand_change_pct,
        )

        scenario_demand_std = Scenario.apply_percentage(
            demand_std,
            scenario.demand_change_pct,
        )

        scenario_lead_time = Scenario.apply_percentage(
            lead_time_days,
            scenario.lead_time_change_pct,
        )

        scenario_inventory = Scenario.apply_percentage(
            current_inventory,
            scenario.inventory_change_pct,
        )

        scenario_annual_demand = Scenario.apply_percentage(
            annual_demand,
            scenario.demand_change_pct,
        )

        simulated = InventoryService.calculate(
            average_daily_demand=scenario_daily_demand,
            demand_std=scenario_demand_std,
            lead_time_days=scenario_lead_time,
            current_inventory=scenario_inventory,
            annual_demand=scenario_annual_demand,
            ordering_cost=ordering_cost,
            holding_cost=holding_cost,
            service_level_z=service_level_z,
        )

        metrics = {}

        for field in (
            "safety_stock",
            "reorder_point",
            "economic_order_quantity",
            "days_of_inventory",
        ):
            baseline_value = baseline[field]
            scenario_value = simulated[field]

            if baseline_value == float("inf"):
                change = 0.0
            else:
                change = percentage_change(
                    float(baseline_value),
                    float(scenario_value),
                )

            metrics[field] = {
                "baseline": baseline_value,
                "scenario": scenario_value,
                "change_pct": change,
                "impact": impact_level(change),
            }

        return {
            "scenario": {
                "name": scenario.name,
                "demand_change_pct": scenario.demand_change_pct,
                "lead_time_change_pct": scenario.lead_time_change_pct,
                "inventory_change_pct": scenario.inventory_change_pct,
            },
            "baseline": baseline,
            "simulated": simulated,
            "impact": metrics,
        }
