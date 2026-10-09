from __future__ import annotations

from statistics import variance
from typing import Sequence


class BullwhipService:
    """
    Bullwhip Effect analytics.

    Bullwhip ratio = upstream order variance / downstream demand variance.

    Ratio:
        <= 1.0  -> low
        <= 1.5  -> moderate
        <= 2.0  -> high
        >  2.0  -> critical
    """

    @staticmethod
    def _validate_series(
        name: str,
        values: Sequence[float],
    ) -> list[float]:
        if values is None:
            raise ValueError(f"{name} is required")

        if len(values) < 2:
            raise ValueError(
                f"{name} must contain at least 2 data points"
            )

        result = [float(value) for value in values]

        if any(value < 0 for value in result):
            raise ValueError(
                f"{name} cannot contain negative values"
            )

        return result

    @staticmethod
    def _variance(values: Sequence[float]) -> float:
        if len(values) < 2:
            return 0.0

        return variance(values)

    @staticmethod
    def _ratio(
        downstream_variance: float,
        upstream_variance: float,
    ) -> float:
        # If downstream demand is perfectly stable:
        # upstream variability is effectively the bullwhip.
        if downstream_variance == 0:
            if upstream_variance == 0:
                return 1.0
            return float("inf")

        return upstream_variance / downstream_variance

    @staticmethod
    def severity(ratio: float) -> str:
        if ratio <= 1.0:
            return "low"

        if ratio <= 1.5:
            return "moderate"

        if ratio <= 2.0:
            return "high"

        return "critical"

    @staticmethod
    def recommendation(ratio: float) -> str:
        severity = BullwhipService.severity(ratio)

        recommendations = {
            "low": (
                "Supply-chain variability is controlled. "
                "Continue monitoring demand and order patterns."
            ),
            "moderate": (
                "Moderate amplification detected. "
                "Improve demand sharing and replenishment coordination."
            ),
            "high": (
                "High order amplification detected. "
                "Review forecasting, safety stock, batch ordering, "
                "and replenishment policies."
            ),
            "critical": (
                "Critical bullwhip effect detected. "
                "Immediately review forecasting, order batching, "
                "lead times, inventory policies, and information sharing."
            ),
        }

        return recommendations[severity]

    @staticmethod
    def evaluate(
        customer_demand: Sequence[float],
        retailer_orders: Sequence[float],
        distributor_orders: Sequence[float],
        manufacturer_orders: Sequence[float],
    ) -> dict:
        customer = BullwhipService._validate_series(
            "customer_demand",
            customer_demand,
        )

        retailer = BullwhipService._validate_series(
            "retailer_orders",
            retailer_orders,
        )

        distributor = BullwhipService._validate_series(
            "distributor_orders",
            distributor_orders,
        )

        manufacturer = BullwhipService._validate_series(
            "manufacturer_orders",
            manufacturer_orders,
        )

        lengths = {
            len(customer),
            len(retailer),
            len(distributor),
            len(manufacturer),
        }

        if len(lengths) != 1:
            raise ValueError(
                "All demand/order series must have the same number of data points"
            )

        customer_variance = BullwhipService._variance(customer)
        retailer_variance = BullwhipService._variance(retailer)
        distributor_variance = BullwhipService._variance(distributor)
        manufacturer_variance = BullwhipService._variance(manufacturer)

        retailer_ratio = BullwhipService._ratio(
            customer_variance,
            retailer_variance,
        )

        distributor_ratio = BullwhipService._ratio(
            customer_variance,
            distributor_variance,
        )

        manufacturer_ratio = BullwhipService._ratio(
            customer_variance,
            manufacturer_variance,
        )

        ratios = [
            retailer_ratio,
            distributor_ratio,
            manufacturer_ratio,
        ]

        finite_ratios = [
            value for value in ratios
            if value != float("inf")
        ]

        if finite_ratios:
            overall_ratio = max(finite_ratios)
        else:
            overall_ratio = float("inf")

        severity = BullwhipService.severity(overall_ratio)

        recommendations = [
            BullwhipService.recommendation(overall_ratio)
        ]

        if retailer_ratio > 1.0:
            recommendations.append(
                "Retailer ordering variability exceeds customer-demand variability."
            )

        if distributor_ratio > retailer_ratio:
            recommendations.append(
                "Distributor amplification exceeds retailer amplification."
            )

        if manufacturer_ratio > distributor_ratio:
            recommendations.append(
                "Manufacturer amplification exceeds distributor amplification."
            )

        return {
            "customer_variance": round(customer_variance, 4),
            "retailer_variance": round(retailer_variance, 4),
            "distributor_variance": round(distributor_variance, 4),
            "manufacturer_variance": round(manufacturer_variance, 4),
            "retailer_bullwhip_ratio": (
                round(retailer_ratio, 4)
                if retailer_ratio != float("inf")
                else None
            ),
            "distributor_bullwhip_ratio": (
                round(distributor_ratio, 4)
                if distributor_ratio != float("inf")
                else None
            ),
            "manufacturer_bullwhip_ratio": (
                round(manufacturer_ratio, 4)
                if manufacturer_ratio != float("inf")
                else None
            ),
            "overall_bullwhip_ratio": (
                round(overall_ratio, 4)
                if overall_ratio != float("inf")
                else None
            ),
            "severity": severity,
            "interpretation": (
                "Critical amplification"
                if severity == "critical"
                else
                "High amplification"
                if severity == "high"
                else
                "Moderate amplification"
                if severity == "moderate"
                else
                "Low or controlled amplification"
            ),
            "recommendations": recommendations,
        }
