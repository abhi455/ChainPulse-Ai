def supplier_risk_level(score: float) -> str:
    if not 0 <= score <= 100:
        raise ValueError(
            "score must be between 0 and 100"
        )

    if score >= 85:
        return "low"

    if score >= 70:
        return "medium"

    if score >= 50:
        return "high"

    return "critical"


def supplier_recommendation(score: float) -> str:
    risk = supplier_risk_level(score)

    recommendations = {
        "low": "Preferred supplier",
        "medium": "Monitor supplier performance",
        "high": "Consider backup supplier",
        "critical": "Avoid dependency and initiate supplier review",
    }

    return recommendations[risk]
