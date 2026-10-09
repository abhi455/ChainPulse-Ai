from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.forecast import Forecast
from backend.database.repositories.base import BaseRepository


class ForecastRepository(BaseRepository[Forecast]):
    def __init__(self, session: Session):
        super().__init__(session, Forecast)

    def get_for_product(
        self,
        product_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Forecast]:
        statement = select(Forecast).where(
            Forecast.product_id == product_id
        )

        if start_date:
            statement = statement.where(Forecast.forecast_date >= start_date)

        if end_date:
            statement = statement.where(Forecast.forecast_date <= end_date)

        statement = statement.order_by(Forecast.forecast_date)

        return list(self.session.scalars(statement).all())
