from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.supplier import Supplier
from backend.database.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, session: Session):
        super().__init__(session, Supplier)

    def get_by_code(self, code: str) -> Supplier | None:
        return self.session.scalar(
            select(Supplier).where(Supplier.code == code)
        )

    def get_by_organization(self, organization_id: str) -> list[Supplier]:
        return list(
            self.session.scalars(
                select(Supplier).where(
                    Supplier.organization_id == organization_id
                )
            ).all()
        )
