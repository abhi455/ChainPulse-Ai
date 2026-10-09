from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.database.models import (
    Product,
    DemandRecord,
    InventoryRecord,
    Forecast,
)

from backend.forecasting.services.forecast_service import (
    ForecastService,
)


class IntelligencePipelineService:

    def __init__(self, db: Session):
        self.db = db

    def _products(self, organization_id: str):
        return (
            self.db.query(Product)
            .filter(
                Product.organization_id == organization_id,
                Product.active == True,
            )
            .order_by(Product.sku)
            .all()
        )

    def _demand(self, product_id: str):
        return (
            self.db.query(DemandRecord)
            .filter(
                DemandRecord.product_id == product_id
            )
            .order_by(DemandRecord.date)
            .all()
        )

    def _inventory(self, product_id: str):
        return (
            self.db.query(InventoryRecord)
            .filter(
                InventoryRecord.product_id == product_id
            )
            .order_by(
                InventoryRecord.date.desc()
            )
            .first()
        )

    def _persist_forecast(
        self,
        product_id: str,
        values: list[float],
        model_name: str,
    ):

        today = date.today()

        existing = (
            self.db.query(Forecast)
            .filter(
                Forecast.product_id == product_id,
                Forecast.model_name == model_name,
                Forecast.forecast_date >= today,
            )
            .all()
        )

        for row in existing:
            self.db.delete(row)

        for index, value in enumerate(values, start=1):

            forecast = Forecast(
                id=str(uuid4()),
                product_id=product_id,
                forecast_date=today + timedelta(days=index),
                predicted_demand=max(
                    0.0,
                    float(value),
                ),
                lower_bound=max(
                    0.0,
                    float(value) * 0.8,
                ),
                upper_bound=max(
                    0.0,
                    float(value) * 1.2,
                ),
                model_name=model_name,
            )

            self.db.add(forecast)

    def _risk(
        self,
        product: Product,
        demand,
        inventory,
    ):

        if inventory is None:
            return {
                "score": 75.0,
                "level": "high",
                "driver": "missing_inventory",
            }

        recent_demand = [
            float(x.quantity or 0)
            for x in demand[-7:]
        ]

        avg_demand = (
            mean(recent_demand)
            if recent_demand
            else 0.0
        )

        available = max(
            0.0,
            float(inventory.on_hand or 0)
            - float(inventory.reserved or 0),
        )

        reorder_point = float(
            inventory.reorder_point or 0
        )

        safety_stock = float(
            inventory.safety_stock or 0
        )

        score = 0.0
        driver = "stable"

        if available <= 0:
            score += 60
            driver = "stockout"

        elif available < safety_stock:
            score += 45
            driver = "below_safety_stock"

        elif available < reorder_point:
            score += 30
            driver = "below_reorder_point"

        if avg_demand > 0:
            coverage = available / avg_demand

            if coverage < 1:
                score += 35
                driver = "low_demand_coverage"

            elif coverage < 2:
                score += 15

        score = min(
            100.0,
            score,
        )

        if score >= 70:
            level = "high"
        elif score >= 40:
            level = "medium"
        else:
            level = "low"

        return {
            "score": round(score, 2),
            "level": level,
            "driver": driver,
            "available_inventory": round(
                available,
                2,
            ),
            "average_daily_demand": round(
                avg_demand,
                2,
            ),
        }

    def _decision(
        self,
        product: Product,
        risk: dict,
        inventory,
    ):

        if inventory is None:
            return {
                "action": "investigate",
                "priority": "high",
                "reason": "Inventory data unavailable.",
            }

        available = float(
            inventory.on_hand or 0
        ) - float(
            inventory.reserved or 0
        )

        reorder_point = float(
            inventory.reorder_point or 0
        )

        if available <= 0:
            action = "urgent_replenishment"
            priority = "critical"

        elif available < reorder_point:
            action = "replenish"
            priority = "high"

        elif risk["level"] == "medium":
            action = "monitor"
            priority = "medium"

        else:
            action = "maintain"
            priority = "low"

        return {
            "action": action,
            "priority": priority,
            "reason": risk["driver"],
            "available_inventory": round(
                available,
                2,
            ),
            "reorder_point": round(
                reorder_point,
                2,
            ),
        }

    def run_product(
        self,
        organization_id: str,
        product: Product,
        periods: int = 7,
        window: int = 3,
    ):

        demand = self._demand(product.id)

        inventory = self._inventory(product.id)

        values = [
            float(row.quantity or 0)
            for row in demand
        ]

        moving_average = []
        exponential = []

        if values:

            if len(values) < window:
                effective_window = max(
                    1,
                    len(values),
                )
            else:
                effective_window = window

            moving_average = ForecastService.moving_average(
                values,
                periods,
                effective_window,
            )

            exponential = ForecastService.exponential_smoothing(
                values,
                periods,
            )

            self._persist_forecast(
                product.id,
                moving_average,
                "moving_average",
            )

            self._persist_forecast(
                product.id,
                exponential,
                "exponential_smoothing",
            )

        risk = self._risk(
            product,
            demand,
            inventory,
        )

        decision = self._decision(
            product,
            risk,
            inventory,
        )

        return {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "demand_records": len(demand),
            "inventory_available": (
                None
                if inventory is None
                else round(
                    float(inventory.on_hand or 0)
                    - float(inventory.reserved or 0),
                    2,
                )
            ),
            "forecast": {
                "periods": periods,
                "moving_average": moving_average,
                "exponential_smoothing": exponential,
            },
            "risk": risk,
            "decision": decision,
        }

    def run(
        self,
        organization_id: str,
        periods: int = 7,
        window: int = 3,
    ):

        products = self._products(
            organization_id
        )

        results = []

        for product in products:
            results.append(
                self.run_product(
                    organization_id,
                    product,
                    periods,
                    window,
                )
            )

        self.db.commit()

        high_risk = [
            x for x in results
            if x["risk"]["level"] == "high"
        ]

        medium_risk = [
            x for x in results
            if x["risk"]["level"] == "medium"
        ]

        return {
            "success": True,
            "organization_id": organization_id,
            "products_processed": len(results),
            "high_risk_products": len(high_risk),
            "medium_risk_products": len(medium_risk),
            "results": results,
        }
