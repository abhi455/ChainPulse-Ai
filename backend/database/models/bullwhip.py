from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy import Date, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.database import Base


class BullwhipRecord(Base):
    __tablename__ = "bullwhip_records"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "date",
            name="uq_bullwhip_org_date",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    customer_demand: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    retailer_orders: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    distributor_orders: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    manufacturer_orders: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
