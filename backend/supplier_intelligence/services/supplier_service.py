from backend.supplier_intelligence.metrics import (
    supplier_recommendation,
    supplier_risk_level,
)
from backend.supplier_intelligence.models import SupplierScorer


class SupplierService:

    @staticmethod
    def evaluate(
        on_time_rate: float,
        defect_rate: float,
        actual_lead_time_days: float,
        expected_lead_time_days: float,
        supplier_cost: float,
        benchmark_cost: float,
    ) -> dict[str, float | str]:

        reliability = SupplierScorer.reliability_score(
            on_time_rate
        )

        quality = SupplierScorer.quality_score(
            defect_rate
        )

        lead_time = SupplierScorer.lead_time_score(
            actual_lead_time_days,
            expected_lead_time_days,
        )

        cost = SupplierScorer.cost_score(
            supplier_cost,
            benchmark_cost,
        )

        overall = SupplierScorer.overall_score(
            reliability,
            quality,
            lead_time,
            cost,
        )

        return {
            "reliability_score": reliability,
            "quality_score": quality,
            "lead_time_score": lead_time,
            "cost_score": cost,
            "overall_score": overall,
            "risk_level": supplier_risk_level(overall),
            "recommendation": supplier_recommendation(overall),
        }
