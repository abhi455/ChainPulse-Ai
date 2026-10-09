def percentage_change(
    baseline: float,
    scenario: float,
) -> float:
    if baseline == 0:
        return 0.0 if scenario == 0 else 100.0

    return round(
        ((scenario - baseline) / abs(baseline)) * 100,
        2,
    )


def impact_level(change_pct: float) -> str:
    magnitude = abs(change_pct)

    if magnitude < 5:
        return "low"

    if magnitude < 15:
        return "medium"

    if magnitude < 30:
        return "high"

    return "critical"
