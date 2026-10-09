from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenarios.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    bullwhip_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    service_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    inventory_impact: Mapped[float | None] = mapped_column(Float, nullable=True)
    results: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    scenario: Mapped["Scenario"] = relationship(back_populates="simulation_runs")
