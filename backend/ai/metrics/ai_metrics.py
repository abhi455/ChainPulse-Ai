def confidence_level(confidence: float) -> str:
    if not 0 <= confidence <= 100:
        raise ValueError(
            "confidence must be between 0 and 100"
        )

    if confidence >= 90:
        return "very_high"

    if confidence >= 75:
        return "high"

    if confidence >= 50:
        return "medium"

    return "low"
