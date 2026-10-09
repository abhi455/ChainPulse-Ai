class SupplierScorer:

    @staticmethod
    def reliability_score(on_time_rate: float) -> float:
        if not 0 <= on_time_rate <= 1:
            raise ValueError("on_time_rate must be between 0 and 1")
        return round(on_time_rate * 100, 2)

    @staticmethod
    def quality_score(defect_rate: float) -> float:
        if not 0 <= defect_rate <= 1:
            raise ValueError("defect_rate must be between 0 and 1")
        return round((1 - defect_rate) * 100, 2)

    @staticmethod
    def lead_time_score(
        actual_lead_time_days: float,
        expected_lead_time_days: float,
    ) -> float:
        if actual_lead_time_days < 0:
            raise ValueError("actual_lead_time_days cannot be negative")

        if expected_lead_time_days <= 0:
            raise ValueError("expected_lead_time_days must be positive")

        if actual_lead_time_days == 0:
            return 100.0

        ratio = actual_lead_time_days / expected_lead_time_days

        return round(
            max(0.0, min(100.0, 100 / ratio)),
            2,
        )

    @staticmethod
    def cost_score(
        supplier_cost: float,
        benchmark_cost: float,
    ) -> float:
        if supplier_cost < 0:
            raise ValueError("supplier_cost cannot be negative")

        if benchmark_cost <= 0:
            raise ValueError("benchmark_cost must be positive")

        if supplier_cost == 0:
            return 100.0

        ratio = supplier_cost / benchmark_cost

        return round(
            max(0.0, min(100.0, 100 / ratio)),
            2,
        )

    @staticmethod
    def overall_score(
        reliability_score: float,
        quality_score: float,
        lead_time_score: float,
        cost_score: float,
    ) -> float:
        scores = [
            reliability_score,
            quality_score,
            lead_time_score,
            cost_score,
        ]

        if any(score < 0 or score > 100 for score in scores):
            raise ValueError(
                "All supplier scores must be between 0 and 100"
            )

        return round(
            reliability_score * 0.35
            + quality_score * 0.25
            + lead_time_score * 0.25
            + cost_score * 0.15,
            2,
        )
