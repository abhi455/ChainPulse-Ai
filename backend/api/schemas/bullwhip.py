from pydantic import BaseModel, Field, model_validator


class BullwhipRequest(BaseModel):
    customer_demand: list[float] = Field(min_length=2)
    retailer_orders: list[float] = Field(min_length=2)
    distributor_orders: list[float] = Field(min_length=2)
    manufacturer_orders: list[float] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_series(self):
        series = {
            "customer_demand": self.customer_demand,
            "retailer_orders": self.retailer_orders,
            "distributor_orders": self.distributor_orders,
            "manufacturer_orders": self.manufacturer_orders,
        }

        lengths = {len(values) for values in series.values()}

        if len(lengths) != 1:
            raise ValueError(
                "All demand/order series must have the same number of data points"
            )

        for name, values in series.items():
            if any(value < 0 for value in values):
                raise ValueError(
                    f"{name} cannot contain negative values"
                )

        return self


class BullwhipResponse(BaseModel):
    customer_variance: float
    retailer_variance: float
    distributor_variance: float
    manufacturer_variance: float

    retailer_bullwhip_ratio: float | None
    distributor_bullwhip_ratio: float | None
    manufacturer_bullwhip_ratio: float | None
    overall_bullwhip_ratio: float | None

    severity: str
    interpretation: str
    recommendations: list[str]
