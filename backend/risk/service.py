from __future__ import annotations

from typing import Any


class RiskService:
    """
    Deterministic risk aggregation service.

    Risk levels:
        low      -> 25
        medium   -> 50
        high     -> 75
        critical -> 100
    """

    LEVEL_SCORES: dict[str, float] = {
        "low": 25.0,
        "medium": 50.0,
        "high": 75.0,
        "critical": 100.0,
    }

    @classmethod
    def evaluate(
        cls,
        components: dict[str, str],
    ) -> dict[str, Any]:
        if not components:
            raise ValueError("At least one risk component is required.")

        normalized: dict[str, str] = {}

        for component, level in components.items():
            component_name = str(component).strip().lower()
            normalized_level = str(level).strip().lower()

            if not component_name:
                raise ValueError("Risk component names cannot be empty.")

            if normalized_level not in cls.LEVEL_SCORES:
                raise ValueError(
                    f"Invalid risk level '{level}' for component "
                    f"'{component}'. Allowed levels: "
                    f"{', '.join(cls.LEVEL_SCORES)}."
                )

            normalized[component_name] = normalized_level

        details = [
            {
                "component": component,
                "score": cls.LEVEL_SCORES[level],
                "level": level,
            }
            for component, level in normalized.items()
        ]

        overall_score = round(
            sum(item["score"] for item in details) / len(details),
            2,
        )

        if overall_score >= 85:
            risk_level = "critical"
        elif overall_score >= 65:
            risk_level = "high"
        elif overall_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"

        highest_score = max(item["score"] for item in details)

        primary_drivers = [
            item["component"]
            for item in details
            if item["score"] == highest_score
        ]

        return {
            "overall_score": overall_score,
            "risk_level": risk_level,
            "primary_drivers": primary_drivers,
            "component_details": details,
        }
