from collections.abc import Sequence

import numpy as np


class ExponentialSmoothingForecaster:
    def __init__(self, alpha: float = 0.3) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")

        self.alpha = alpha

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

        level = float(data[0])

        for value in data[1:]:
            level = (
                self.alpha * float(value)
                + (1 - self.alpha) * level
            )

        prediction = max(0.0, level)

        return [prediction] * periods
