from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base


class InventoryRecord(Base):
    __tablename__ = "inventory_records"

    __table_args__ = (
        UniqueConstraint("product_id", "date", name="uq_product_inventory_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reserved: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    safety_stock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stockout: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    product: Mapped["Product"] = relationship(back_populates="inventory_records")
