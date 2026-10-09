from __future__ import annotations

from backend.forecasting.core.exponential_smoothing import (
    ExponentialSmoothingForecaster,
)
from backend.forecasting.core.moving_average import (
    MovingAverageForecaster,
)


class ForecastService:
    """Unified forecasting service used by the API."""

    @staticmethod
    def moving_average(
        values: list[float],
        periods: int,
        window: int,
    ) -> list[float]:
        return MovingAverageForecaster.forecast(
            values=values,
            horizon=periods,
            window=window,
        )

    @staticmethod
    def exponential_smoothing(
        values: list[float],
        periods: int,
    ) -> list[float]:
        return ExponentialSmoothingForecaster.forecast(
            values=values,
            horizon=periods,
            alpha=0.3,
        )
