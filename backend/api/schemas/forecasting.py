from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    values: list[float] = Field(..., min_length=1)
    periods: int = Field(default=7, ge=1)
    window: int = Field(default=3, ge=1)


class ProductForecastRequest(BaseModel):
    periods: int = Field(default=7, ge=1)
    window: int = Field(default=3, ge=1)


class ProductForecastResponse(BaseModel):
    product_id: str
    data_points: int
    moving_average: list[float]
    exponential_smoothing: list[float]


class ForecastResponse(BaseModel):
    model: str
    forecasts: list[float]