from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.demand import DemandRecord
from backend.database.repositories.base import BaseRepository


class DemandRepository(BaseRepository[DemandRecord]):
    def __init__(self, session: Session):
        super().__init__(session, DemandRecord)

    def get_for_product(
        self,
        product_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DemandRecord]:
        statement = select(DemandRecord).where(
            DemandRecord.product_id == product_id
        )

        if start_date:
            statement = statement.where(DemandRecord.date >= start_date)

        if end_date:
            statement = statement.where(DemandRecord.date <= end_date)

        statement = statement.order_by(DemandRecord.date)

        return list(self.session.scalars(statement).all())
