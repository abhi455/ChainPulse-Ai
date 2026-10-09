from __future__ import annotations

from statistics import mean, stdev


class InventoryOptimizer:
    """Core inventory optimization calculations."""

    @staticmethod
    def optimize(
        demand: list[float],
        current_inventory: float,
        lead_time: float,
        service_level_z: float = 1.65,
        target_inventory_days: float | None = None,
    ):
        if not demand:
            raise ValueError("Demand history cannot be empty.")

        if current_inventory < 0:
            raise ValueError("Current inventory cannot be negative.")

        if lead_time < 0:
            raise ValueError("Lead time cannot be negative.")

        if service_level_z < 0:
            raise ValueError("Service-level z-score cannot be negative.")

        values = [float(value) for value in demand]

        average_demand = mean(values)

        demand_std = (
            stdev(values)
            if len(values) > 1
            else 0.0
        )

        safety_stock = (
            service_level_z
            * demand_std
            * (lead_time ** 0.5)
        )

        lead_time_demand = average_demand * lead_time

        reorder_point = (
            lead_time_demand
            + safety_stock
        )

        if target_inventory_days is None:
            target_inventory_days = max(
                lead_time * 2,
                7.0,
            )

        target_inventory = (
            average_demand
            * target_inventory_days
        )

        inventory_position = current_inventory

        recommended_order_quantity = max(
            0.0,
            target_inventory - inventory_position,
        )

        if current_inventory <= 0:
            decision = "STOCKOUT_RISK"
            risk_level = "critical"

        elif current_inventory < reorder_point:
            decision = "REORDER_NOW"
            risk_level = "high"

        elif current_inventory < target_inventory:
            decision = "REORDER_SOON"
            risk_level = "medium"

        else:
            decision = "HOLD"
            risk_level = "low"

        return {
            "average_demand": round(average_demand, 4),
            "demand_std": round(demand_std, 4),
            "safety_stock": round(safety_stock, 4),
            "reorder_point": round(reorder_point, 4),
            "recommended_order_quantity": round(
                recommended_order_quantity,
                4,
            ),
            "inventory_position": round(
                inventory_position,
                4,
            ),
            "decision": decision,
            "risk_level": risk_level,
        }
