from datetime import date

from sqlalchemy.orm import Session

from backend.database.models import InventoryRecord, Product
from backend.database.repositories import InventoryRepository


class InventoryRecordService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = InventoryRepository(session)

    def create(
        self,
        product: Product,
        record_date: date,
        on_hand: float,
        reserved: float = 0.0,
        safety_stock: float = 0.0,
        reorder_point: float = 0.0,
    ) -> InventoryRecord:

        if on_hand < 0:
            raise ValueError("on_hand cannot be negative")

        if reserved < 0:
            raise ValueError("reserved cannot be negative")

        if reserved > on_hand:
            raise ValueError(
                "reserved cannot exceed on_hand"
            )

        if safety_stock < 0:
            raise ValueError("safety_stock cannot be negative")

        if reorder_point < 0:
            raise ValueError("reorder_point cannot be negative")

        existing = self.repository.get_by_product_and_date(
            product.id,
            record_date,
        )

        if existing is not None:
            raise ValueError(
                f"Inventory record already exists for product "
                f"'{product.id}' on {record_date}"
            )

        available = max(on_hand - reserved, 0.0)

        record = InventoryRecord(
            product_id=product.id,
            date=record_date,
            on_hand=on_hand,
            reserved=reserved,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            stockout=available <= 0,
        )

        return self.repository.add(record)

    def list_for_product(
        self,
        product_id: str,
    ) -> list[InventoryRecord]:
        return self.repository.get_for_product(product_id)
