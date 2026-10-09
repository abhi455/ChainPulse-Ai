from __future__ import annotations

from statistics import mean


class MovingAverageForecaster:
    """Simple moving-average forecasting engine."""

    @staticmethod
    def forecast(
        values: list[float],
        horizon: int,
        window: int,
    ) -> list[float]:
        if not values:
            raise ValueError("At least one historical value is required.")

        if horizon < 1:
            raise ValueError("Forecast horizon must be at least 1.")

        if window < 1:
            raise ValueError("Window must be at least 1.")

        if window > len(values):
            raise ValueError(
                "Window cannot be larger than the number of historical values."
            )

        history = [float(value) for value in values]
        forecasts: list[float] = []

        for _ in range(horizon):
            prediction = mean(history[-window:])
            prediction = round(max(0.0, prediction), 4)
            forecasts.append(prediction)
            history.append(prediction)

        return forecasts
