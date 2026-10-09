def risk_score(
    stockout_risk: str,
    overstock_risk: str,
    supplier_risk: str,
) -> float:

    weights = {
        "low": 10.0,
        "medium": 40.0,
        "high": 70.0,
        "critical": 100.0,
    }

    risks = [
        weights[stockout_risk],
        weights[overstock_risk],
        weights[supplier_risk],
    ]

    return round(sum(risks) / len(risks), 2)


def risk_level(score: float) -> str:
    if not 0 <= score <= 100:
        raise ValueError(
            "score must be between 0 and 100"
        )

    if score >= 80:
        return "critical"

    if score >= 60:
        return "high"

    if score >= 35:
        return "medium"

    return "low"
