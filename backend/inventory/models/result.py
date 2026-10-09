from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InventoryOptimizationResult:
    average_demand: float
    demand_std: float
    safety_stock: float
    reorder_point: float
    recommended_order_quantity: float
    inventory_position: float
    decision: str
    risk_level: str
