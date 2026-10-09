from __future__ import annotations

from backend.inventory.metrics import (
    overstock_risk,
    stockout_risk,
)
from backend.inventory.models.inventory_calculator import InventoryCalculator


class InventoryService:
    """Inventory planning, optimization, and risk analysis service."""

    @staticmethod
    def calculate(
        average_daily_demand: float,
        demand_std: float,
        lead_time_days: float,
        current_inventory: float,
        annual_demand: float,
        ordering_cost: float,
        holding_cost: float,
        service_level_z: float = 1.65,
    ) -> dict[str, float | str]:

        safety_stock = InventoryCalculator.safety_stock(
            demand_std=demand_std,
            lead_time_days=lead_time_days,
            service_level_z=service_level_z,
        )

        reorder_point = InventoryCalculator.reorder_point(
            average_daily_demand=average_daily_demand,
            lead_time_days=lead_time_days,
            safety_stock=safety_stock,
        )

        economic_order_quantity = (
            InventoryCalculator.economic_order_quantity(
                annual_demand=annual_demand,
                ordering_cost=ordering_cost,
                holding_cost=holding_cost,
            )
        )

        days_of_inventory = InventoryCalculator.days_of_inventory(
            current_inventory=current_inventory,
            average_daily_demand=average_daily_demand,
        )

        return {
            "safety_stock": round(safety_stock, 2),
            "reorder_point": round(reorder_point, 2),
            "economic_order_quantity": round(
                economic_order_quantity,
                2,
            ),
            "days_of_inventory": (
                round(days_of_inventory, 2)
                if days_of_inventory != float("inf")
                else float("inf")
            ),
            "stockout_risk": stockout_risk(
                current_inventory,
                reorder_point,
            ),
            "overstock_risk": overstock_risk(
                current_inventory,
                reorder_point,
                economic_order_quantity,
            ),
        }

