from datetime import date

from sqlalchemy.orm import Session

from backend.database.models import DemandRecord
from backend.database.repositories import DemandRepository


class DemandService:
    def __init__(self, session: Session):
        self.repository = DemandRepository(session)

    def create(
        self,
        product_id: str,
        demand_date: date,
        quantity: float,
        revenue: float = 0.0,
    ) -> DemandRecord:
        product_id = product_id.strip()

        if not product_id:
            raise ValueError("Product ID cannot be empty")

        if quantity < 0:
            raise ValueError("Demand quantity cannot be negative")

        if revenue < 0:
            raise ValueError("Revenue cannot be negative")

        existing = self.repository.get_for_product(
            product_id=product_id,
            start_date=demand_date,
            end_date=demand_date,
        )

        if existing:
            raise ValueError(
                f"Demand record already exists for product '{product_id}' "
                f"on {demand_date}"
            )

        record = DemandRecord(
            product_id=product_id,
            date=demand_date,
            quantity=quantity,
            revenue=revenue,
        )

        return self.repository.add(record)

    def list_for_product(
        self,
        product_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DemandRecord]:
        return self.repository.get_for_product(
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
        )
