from collections.abc import Sequence

from backend.forecasting.metrics import mae, mape, rmse
from backend.forecasting.models import (
    ExponentialSmoothingForecaster,
    MovingAverageForecaster,
)


class ForecastService:

    @staticmethod
    def moving_average(
        values: Sequence[float],
        periods: int,
        window: int = 7,
    ) -> list[float]:
        model = MovingAverageForecaster(window=window)

        return model.forecast(
            values=values,
            periods=periods,
        )

    @staticmethod
    def exponential_smoothing(
        values: Sequence[float],
        periods: int,
        alpha: float = 0.3,
    ) -> list[float]:
        model = ExponentialSmoothingForecaster(alpha=alpha)

        return model.forecast(
            values=values,
            periods=periods,
        )

    @staticmethod
    def evaluate(
        actual: Sequence[float],
        predicted: Sequence[float],
    ) -> dict[str, float]:
        return {
            "mae": mae(actual, predicted),
            "rmse": rmse(actual, predicted),
            "mape": mape(actual, predicted),
        }

    @staticmethod
    def select_best_model(
        actual: Sequence[float],
        moving_average_predictions: Sequence[float],
        exponential_predictions: Sequence[float],
    ) -> str:
        moving_average_error = rmse(
            actual,
            moving_average_predictions,
        )

        exponential_error = rmse(
            actual,
            exponential_predictions,
        )

        if moving_average_error <= exponential_error:
            return "moving_average"

        return "exponential_smoothing"
