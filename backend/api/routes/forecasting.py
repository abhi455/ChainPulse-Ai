from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db
from backend.api.schemas.forecasting import (
    ForecastRequest,
    ForecastResponse,
    ProductForecastRequest,
    ProductForecastResponse,
)
from backend.auth.dependencies import get_current_user
from backend.database.models import Forecast, User
from backend.database.repositories import DemandRepository
from backend.forecasting import ForecastService
from backend.services import ProductService


router = APIRouter(
    prefix="/forecasting",
    tags=["Forecasting"],
)


def _persist_forecasts(
    db: Session,
    product_id: str,
    forecasts: list[float],
    model_name: str,
) -> None:
    """
    Persist the generated forecast horizon for a product.

    Forecast dates start from tomorrow and continue for the
    requested number of periods.

    Existing rows for the same product/model/date are replaced
    so repeated forecast generation remains idempotent.
    """

    if not forecasts:
        return

    start_date = date.today() + timedelta(days=1)

    forecast_dates = [
        start_date + timedelta(days=index)
        for index in range(len(forecasts))
    ]

    existing_rows = (
        db.query(Forecast)
        .filter(
            Forecast.product_id == product_id,
            Forecast.model_name == model_name,
            Forecast.forecast_date >= start_date,
            Forecast.forecast_date <= forecast_dates[-1],
        )
        .all()
    )

    for row in existing_rows:
        db.delete(row)

    for forecast_date, predicted_demand in zip(
        forecast_dates,
        forecasts,
    ):
        db.add(
            Forecast(
                id=str(uuid4()),
                product_id=product_id,
                forecast_date=forecast_date,
                predicted_demand=float(predicted_demand),
                lower_bound=None,
                upper_bound=None,
                model_name=model_name,
                accuracy_score=None,
            )
        )


@router.post(
    "/moving-average",
    response_model=ForecastResponse,
)
def moving_average(
    request: ForecastRequest,
    user: User = Depends(get_current_user),
) -> ForecastResponse:

    forecasts = ForecastService.moving_average(
        values=request.values,
        periods=request.periods,
        window=request.window,
    )

    return ForecastResponse(
        model="moving_average",
        forecasts=forecasts,
    )


@router.post(
    "/exponential-smoothing",
    response_model=ForecastResponse,
)
def exponential_smoothing(
    request: ForecastRequest,
    user: User = Depends(get_current_user),
) -> ForecastResponse:

    forecasts = ForecastService.exponential_smoothing(
        values=request.values,
        periods=request.periods,
    )

    return ForecastResponse(
        model="exponential_smoothing",
        forecasts=forecasts,
    )


@router.post(
    "/product/{product_id}",
    response_model=ProductForecastResponse,
)
def forecast_product(
    product_id: str,
    request: ProductForecastRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProductForecastResponse:

    product = ProductService(db).get(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    if product.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this product.",
        )

    records = DemandRepository(db).get_for_product(product_id)

    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No demand history found for this product.",
        )

    values = [
        float(record.quantity)
        for record in records
    ]

    moving_average_forecasts = ForecastService.moving_average(
        values=values,
        periods=request.periods,
        window=request.window,
    )

    exponential_smoothing_forecasts = (
        ForecastService.exponential_smoothing(
            values=values,
            periods=request.periods,
        )
    )

    # Persist both forecasting models.
    _persist_forecasts(
        db=db,
        product_id=product_id,
        forecasts=moving_average_forecasts,
        model_name="moving_average",
    )

    _persist_forecasts(
        db=db,
        product_id=product_id,
        forecasts=exponential_smoothing_forecasts,
        model_name="exponential_smoothing",
    )

    db.commit()

    return ProductForecastResponse(
        product_id=product_id,
        data_points=len(values),
        moving_average=moving_average_forecasts,
        exponential_smoothing=exponential_smoothing_forecasts,
    )
