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

    def update(
        self,
        record: InventoryRecord,
        *,
        record_date: date | None = None,
        on_hand: float | None = None,
        reserved: float | None = None,
        safety_stock: float | None = None,
        reorder_point: float | None = None,
    ) -> InventoryRecord:
        new_on_hand = (
            record.on_hand
            if on_hand is None
            else on_hand
        )

        new_reserved = (
            record.reserved
            if reserved is None
            else reserved
        )

        if new_on_hand < 0:
            raise ValueError(
                "on_hand cannot be negative"
            )

        if new_reserved < 0:
            raise ValueError(
                "reserved cannot be negative"
            )

        if new_reserved > new_on_hand:
            raise ValueError(
                "reserved cannot exceed on_hand"
            )

        if record_date is not None:
            existing = self.repository.get_by_product_and_date(
                record.product_id,
                record_date,
            )

            if existing is not None and existing.id != record.id:
                raise ValueError(
                    f"Inventory record already exists for "
                    f"product '{record.product_id}' "
                    f"on {record_date}"
                )

            record.date = record_date

        if on_hand is not None:
            record.on_hand = on_hand

        if reserved is not None:
            record.reserved = reserved

        if safety_stock is not None:
            if safety_stock < 0:
                raise ValueError(
                    "safety_stock cannot be negative"
                )
            record.safety_stock = safety_stock

        if reorder_point is not None:
            if reorder_point < 0:
                raise ValueError(
                    "reorder_point cannot be negative"
                )
            record.reorder_point = reorder_point

        record.stockout = (
            max(
                record.on_hand - record.reserved,
                0.0,
            ) <= 0
        )

        return record
