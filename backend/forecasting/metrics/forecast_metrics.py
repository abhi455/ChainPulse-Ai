from collections.abc import Sequence

import numpy as np


def mae(
    actual: Sequence[float],
    predicted: Sequence[float],
) -> float:
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if actual_array.shape != predicted_array.shape:
        raise ValueError("actual and predicted must have the same length")

    if actual_array.size == 0:
        raise ValueError("actual and predicted cannot be empty")

    return float(
        np.mean(np.abs(actual_array - predicted_array))
    )


def rmse(
    actual: Sequence[float],
    predicted: Sequence[float],
) -> float:
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if actual_array.shape != predicted_array.shape:
        raise ValueError("actual and predicted must have the same length")

    if actual_array.size == 0:
        raise ValueError("actual and predicted cannot be empty")

    return float(
        np.sqrt(
            np.mean(
                (actual_array - predicted_array) ** 2
            )
        )
    )


def mape(
    actual: Sequence[float],
    predicted: Sequence[float],
) -> float:
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)

    if actual_array.shape != predicted_array.shape:
        raise ValueError("actual and predicted must have the same length")

    if actual_array.size == 0:
        raise ValueError("actual and predicted cannot be empty")

    non_zero = actual_array != 0

    if not np.any(non_zero):
        return 0.0

    return float(
        np.mean(
            np.abs(
                (
                    actual_array[non_zero]
                    - predicted_array[non_zero]
                )
                / actual_array[non_zero]
            )
        )
        * 100
    )
