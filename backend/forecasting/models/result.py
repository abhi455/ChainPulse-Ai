from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ForecastResult:
    method: str
    historical_values: list[float]
    forecast_values: list[float]
    horizon: int
    confidence: float
    warnings: list[str] = field(default_factory=list)
