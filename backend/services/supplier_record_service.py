from __future__ import annotations

from sqlalchemy.orm import Session

from backend.database.models import Supplier
from backend.database.repositories import SupplierRepository


class SupplierRecordService:
    def __init__(self, session: Session):
        self.repository = SupplierRepository(session)

    def create(
        self,
        organization_id: str,
        name: str,
        code: str,
        lead_time_days: int = 7,
        reliability_score: float = 1.0,
    ) -> Supplier:
        name = name.strip()
        code = code.strip()

        if not name:
            raise ValueError(
                "Supplier name cannot be empty."
            )

        if not code:
            raise ValueError(
                "Supplier code cannot be empty."
            )

        if lead_time_days < 0:
            raise ValueError(
                "Lead time cannot be negative."
            )

        if not 0 <= reliability_score <= 1:
            raise ValueError(
                "Reliability score must be between 0 and 1."
            )

        if self.repository.get_by_code(
            code,
            organization_id,
        ) is not None:
            raise ValueError(
                f"Supplier with code '{code}' already exists."
            )

        supplier = Supplier(
            organization_id=organization_id,
            name=name,
            code=code,
            lead_time_days=lead_time_days,
            reliability_score=reliability_score,
        )

        return self.repository.add(supplier)

    def get(
        self,
        supplier_id: str,
    ) -> Supplier | None:
        return self.repository.get_by_id(supplier_id)

    def get_for_organization(
        self,
        supplier_id: str,
        organization_id: str,
    ) -> Supplier | None:
        return self.repository.get_by_id_for_organization(
            supplier_id,
            organization_id,
        )

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[Supplier]:
        return self.repository.get_by_organization(
            organization_id
        )

    def update(
        self,
        supplier: Supplier,
        *,
        name: str | None = None,
        code: str | None = None,
        lead_time_days: int | None = None,
        reliability_score: float | None = None,
    ) -> Supplier:
        if name is not None:
            name = name.strip()

            if not name:
                raise ValueError(
                    "Supplier name cannot be empty."
                )

            supplier.name = name

        if code is not None:
            code = code.strip()

            if not code:
                raise ValueError(
                    "Supplier code cannot be empty."
                )

            existing = self.repository.get_by_code(
                code,
                supplier.organization_id,
            )

            if (
                existing is not None
                and existing.id != supplier.id
            ):
                raise ValueError(
                    f"Supplier with code '{code}' already exists."
                )

            supplier.code = code

        if lead_time_days is not None:
            if lead_time_days < 0:
                raise ValueError(
                    "Lead time cannot be negative."
                )
            supplier.lead_time_days = lead_time_days

        if reliability_score is not None:
            if not 0 <= reliability_score <= 1:
                raise ValueError(
                    "Reliability score must be between 0 and 1."
                )
            supplier.reliability_score = reliability_score

        return supplier


