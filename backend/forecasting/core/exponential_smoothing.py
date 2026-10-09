from __future__ import annotations


class ExponentialSmoothingForecaster:
    """Simple single exponential-smoothing forecaster."""

    @staticmethod
    def forecast(
        values: list[float],
        horizon: int,
        alpha: float = 0.3,
    ) -> list[float]:
        if not values:
            raise ValueError("At least one historical value is required.")

        if horizon < 1:
            raise ValueError("Forecast horizon must be at least 1.")

        if not 0.0 < alpha <= 1.0:
            raise ValueError("Alpha must be greater than 0 and at most 1.")

        history = [float(value) for value in values]

        smoothed = history[0]

        for value in history[1:]:
            smoothed = (
                alpha * value
                + (1.0 - alpha) * smoothed
            )

        prediction = round(max(0.0, smoothed), 4)

        return [prediction] * horizon
