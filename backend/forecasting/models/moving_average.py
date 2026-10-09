from collections.abc import Sequence

import numpy as np


class MovingAverageForecaster:
    def __init__(self, window: int = 7) -> None:
        if window < 1:
            raise ValueError("window must be at least 1")

        self.window = window

    def forecast(
        self,
        values: Sequence[float],
        periods: int,
    ) -> list[float]:
        if periods < 1:
            raise ValueError("periods must be at least 1")

        data = np.asarray(values, dtype=float)

        if data.size == 0:
            raise ValueError("values cannot be empty")

        if np.isnan(data).any():
            raise ValueError("values cannot contain NaN")

        history = data.tolist()
        forecasts: list[float] = []

        for _ in range(periods):
            recent = history[-self.window:]
            prediction = float(np.mean(recent))

            prediction = max(0.0, prediction)

            forecasts.append(prediction)
            history.append(prediction)

        return forecasts
