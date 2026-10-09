from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.inventory import InventoryRecord
from backend.database.models.product import Product
from backend.database.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryRecord]):
    def __init__(self, session: Session):
        super().__init__(session, InventoryRecord)

    def get_for_product(
        self,
        product_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[InventoryRecord]:
        statement = select(InventoryRecord).where(
            InventoryRecord.product_id == product_id
        )

        if start_date:
            statement = statement.where(
                InventoryRecord.date >= start_date
            )

        if end_date:
            statement = statement.where(
                InventoryRecord.date <= end_date
            )

        statement = statement.order_by(InventoryRecord.date)

        return list(
            self.session.scalars(statement).all()
        )

    def get_by_product_and_date(
        self,
        product_id: str,
        record_date: date,
    ) -> InventoryRecord | None:
        return self.session.scalar(
            select(InventoryRecord).where(
                InventoryRecord.product_id == product_id,
                InventoryRecord.date == record_date,
            )
        )

    def get_by_id_for_organization(
        self,
        inventory_id: str,
        organization_id: str,
    ) -> InventoryRecord | None:
        return self.session.scalar(
            select(InventoryRecord)
            .join(Product, InventoryRecord.product_id == Product.id)
            .where(
                InventoryRecord.id == inventory_id,
                Product.organization_id == organization_id,
            )
        )
