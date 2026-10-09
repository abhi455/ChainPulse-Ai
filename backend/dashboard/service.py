from __future__ import annotations

from statistics import mean
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database.models import (
    DemandRecord,
    Forecast,
    InventoryRecord,
    Product,
    Scenario,
    SimulationRun,
    Supplier,
)
from backend.risk import RiskService


class DashboardService:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _level_from_score(score: float) -> str:
        if score >= 85:
            return "critical"
        if score >= 65:
            return "high"
        if score >= 40:
            return "medium"
        return "low"

    @staticmethod
    def _demand_risk(values: list[float]) -> tuple[float, str]:
        if not values:
            return 25.0, "low"

        avg = mean(values)

        if avg <= 0:
            return 25.0, "low"

        if len(values) < 2:
            return 50.0, "medium"

        deviations = [abs(v - avg) for v in values]
        volatility = mean(deviations) / avg

        if volatility >= 0.50:
            score = 100.0
        elif volatility >= 0.30:
            score = 75.0
        elif volatility >= 0.15:
            score = 50.0
        else:
            score = 25.0

        return score, DashboardService._level_from_score(score)

    @staticmethod
    def _inventory_risk(
        records: list[InventoryRecord],
    ) -> tuple[float, str]:
        if not records:
            return 50.0, "medium"

        latest = records[-1]

        if latest.stockout or latest.on_hand <= 0:
            score = 100.0
        elif latest.reorder_point > 0 and latest.on_hand < latest.reorder_point:
            score = 75.0
        elif (
            latest.reorder_point > 0
            and latest.on_hand < latest.reorder_point * 1.25
        ):
            score = 50.0
        else:
            score = 25.0

        return score, DashboardService._level_from_score(score)

    @staticmethod
    def _supplier_risk(reliability: float) -> tuple[float, str]:
        if reliability >= 0.90:
            score = 25.0
        elif reliability >= 0.75:
            score = 50.0
        elif reliability >= 0.50:
            score = 75.0
        else:
            score = 100.0

        return score, DashboardService._level_from_score(score)

    def summary(self, organization_id: str) -> dict[str, Any]:
        products = list(
            self.session.scalars(
                select(Product)
                .where(Product.organization_id == organization_id)
                .order_by(Product.created_at)
            ).all()
        )

        product_ids = [p.id for p in products]

        if product_ids:
            demand_records = list(
                self.session.scalars(
                    select(DemandRecord)
                    .where(DemandRecord.product_id.in_(product_ids))
                    .order_by(DemandRecord.date)
                ).all()
            )

            inventory_records = list(
                self.session.scalars(
                    select(InventoryRecord)
                    .where(InventoryRecord.product_id.in_(product_ids))
                    .order_by(
                        InventoryRecord.date,
                        InventoryRecord.id,
                    )
                ).all()
            )

            forecasts = list(
                self.session.scalars(
                    select(Forecast)
                    .where(Forecast.product_id.in_(product_ids))
                    .order_by(Forecast.created_at.desc())
                ).all()
            )
        else:
            demand_records = []
            inventory_records = []
            forecasts = []

        suppliers = list(
            self.session.scalars(
                select(Supplier)
                .where(Supplier.organization_id == organization_id)
            ).all()
        )

        scenarios = list(
            self.session.scalars(
                select(Scenario)
                .where(Scenario.organization_id == organization_id)
                .order_by(Scenario.created_at.desc())
            ).all()
        )

        scenario_ids = [s.id for s in scenarios]

        if scenario_ids:
            simulations = list(
                self.session.scalars(
                    select(SimulationRun)
                    .where(SimulationRun.scenario_id.in_(scenario_ids))
                    .order_by(SimulationRun.started_at.desc())
                ).all()
            )
        else:
            simulations = []

        demand_values = [float(x.quantity) for x in demand_records]

        total_demand = round(sum(demand_values), 2)
        total_revenue = round(
            sum(float(x.revenue) for x in demand_records),
            2,
        )

        average_daily_demand = round(
            mean(demand_values),
            2,
        ) if demand_values else 0.0

        inventory_on_hand = round(
            sum(float(x.on_hand) for x in inventory_records),
            2,
        )

        inventory_reserved = round(
            sum(float(x.reserved) for x in inventory_records),
            2,
        )

        inventory_available = round(
            inventory_on_hand - inventory_reserved,
            2,
        )

        inventory_below_reorder = sum(
            1
            for x in inventory_records
            if x.reorder_point > 0
            and x.on_hand < x.reorder_point
        )

        inventory_stockouts = sum(
            1 for x in inventory_records if x.stockout
        )

        reliability_values = [
            float(x.reliability_score)
            for x in suppliers
        ]

        average_supplier_reliability = round(
            mean(reliability_values) * 100
            if reliability_values
            else 0.0,
            2,
        )

        # ============================================================
        # RISK CALCULATION
        #
        # A brand-new organization has no operational history.
        # Do NOT manufacture a "low" or "medium" risk level from
        # missing data. Risk becomes meaningful only after actual
        # demand, inventory, or supplier data exists.
        # ============================================================

        has_demand_data = bool(demand_values)
        has_inventory_data = bool(inventory_records)
        has_supplier_data = bool(reliability_values)

        if has_demand_data:
            demand_score, demand_risk_level = self._demand_risk(
                demand_values
            )
        else:
            demand_score = 0.0
            demand_risk_level = "N/A"

        if has_inventory_data:
            inventory_score, inventory_risk_level = self._inventory_risk(
                inventory_records
            )
        else:
            inventory_score = 0.0
            inventory_risk_level = "N/A"

        if has_supplier_data:
            supplier_score, supplier_risk_level = self._supplier_risk(
                mean(reliability_values)
            )
        else:
            supplier_score = 0.0
            supplier_risk_level = "N/A"

        # Only evaluate overall risk when at least one real
        # operational risk source exists.
        risk_inputs = {}

        if has_demand_data:
            risk_inputs["demand"] = demand_risk_level

        if has_inventory_data:
            risk_inputs["inventory"] = inventory_risk_level

        if has_supplier_data:
            risk_inputs["supplier"] = supplier_risk_level

        if risk_inputs:
            risk_result = RiskService.evaluate(risk_inputs)
            overall_risk_score = float(
                risk_result.get("overall_score", 0) or 0
            )
            overall_risk_level = str(
                risk_result.get("risk_level", "N/A") or "N/A"
            )
            primary_risk_drivers = risk_result.get(
                "primary_drivers",
                [],
            )
        else:
            overall_risk_score = 0.0
            overall_risk_level = "N/A"
            primary_risk_drivers = []

        alerts: list[str] = []
        recommendations: list[str] = []

        if inventory_stockouts:
            alerts.append(
                f"{inventory_stockouts} inventory record(s) indicate stockout."
            )
            recommendations.append(
                "Review stockout products and replenish before service levels decline."
            )

        if inventory_below_reorder:
            alerts.append(
                f"{inventory_below_reorder} inventory record(s) are below reorder point."
            )
            recommendations.append(
                "Prioritize replenishment for products below reorder point."
            )

        if demand_risk_level in {"high", "critical"}:
            alerts.append(
                f"Demand volatility is {demand_risk_level}."
            )
            recommendations.append(
                "Review demand history and forecast assumptions."
            )

        if supplier_risk_level in {"high", "critical"}:
            alerts.append(
                f"Supplier reliability risk is {supplier_risk_level}."
            )
            recommendations.append(
                "Evaluate backup supplier options."
            )

        # Only report "no major alerts" when there is actual
        # operational data to evaluate.
        if not alerts and risk_inputs:
            alerts.append(
                "No major operational alerts detected."
            )

        latest_scenario_name = (
            scenarios[0].name
            if scenarios
            else None
        )

        latest_simulation_status = (
            simulations[0].status
            if simulations
            else None
        )

        return {
            "organization_id": organization_id,
            "product_count": len(products),
            "active_product_count": sum(
                1 for p in products if p.active
            ),
            "demand_record_count": len(demand_records),
            "inventory_record_count": len(inventory_records),
            "supplier_count": len(suppliers),
            "scenario_count": len(scenarios),
            "simulation_run_count": len(simulations),

            "total_demand_quantity": total_demand,
            "total_revenue": total_revenue,
            "average_daily_demand": average_daily_demand,

            "inventory_on_hand": inventory_on_hand,
            "inventory_reserved": inventory_reserved,
            "inventory_available": inventory_available,
            "inventory_below_reorder": inventory_below_reorder,
            "inventory_stockouts": inventory_stockouts,

            "average_supplier_reliability":
                average_supplier_reliability,
            "supplier_risk_level": supplier_risk_level,

            "demand_risk_level": demand_risk_level,
            "inventory_risk_level": inventory_risk_level,
            "overall_risk_score": overall_risk_score,
            "overall_risk_level": overall_risk_level,
            "primary_risk_drivers": primary_risk_drivers,

            "latest_forecast_count": len(forecasts),
            "latest_scenario_name": latest_scenario_name,
            "latest_simulation_status":
                latest_simulation_status,

            "alerts": alerts,
            "recommendations": recommendations,
        }

    def product(
        self,
        organization_id: str,
        product_id: str,
    ) -> dict[str, Any] | None:

        product = self.session.get(Product, product_id)

        if product is None:
            return None

        if product.organization_id != organization_id:
            return None

        demands = list(
            self.session.scalars(
                select(DemandRecord)
                .where(DemandRecord.product_id == product_id)
                .order_by(DemandRecord.date)
            ).all()
        )

        inventories = list(
            self.session.scalars(
                select(InventoryRecord)
                .where(InventoryRecord.product_id == product_id)
                .order_by(InventoryRecord.date)
            ).all()
        )

        forecasts = list(
            self.session.scalars(
                select(Forecast)
                .where(Forecast.product_id == product_id)
                .order_by(Forecast.created_at.desc())
            ).all()
        )

        demand_values = [float(x.quantity) for x in demands]

        latest_inventory = inventories[-1] if inventories else None
        latest_forecast = forecasts[0] if forecasts else None

        return {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "active": product.active,
            "lead_time_days": product.lead_time_days,

            "demand_record_count": len(demands),
            "total_demand_quantity": round(
                sum(demand_values),
                2,
            ),
            "total_revenue": round(
                sum(float(x.revenue) for x in demands),
                2,
            ),
            "average_daily_demand": round(
                mean(demand_values),
                2,
            ) if demand_values else 0.0,

            "latest_inventory_on_hand":
                float(latest_inventory.on_hand)
                if latest_inventory else None,

            "latest_inventory_reserved":
                float(latest_inventory.reserved)
                if latest_inventory else None,

            "latest_safety_stock":
                float(latest_inventory.safety_stock)
                if latest_inventory else None,

            "latest_reorder_point":
                float(latest_inventory.reorder_point)
                if latest_inventory else None,

            "latest_stockout":
                bool(latest_inventory.stockout)
                if latest_inventory else None,

            "forecast_count": len(forecasts),

            "latest_forecast_demand":
                float(latest_forecast.predicted_demand)
                if latest_forecast else None,

            "latest_forecast_model":
                latest_forecast.model_name
                if latest_forecast else None,
        }


