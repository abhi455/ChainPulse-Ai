from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.supplier import Supplier
from backend.database.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, session: Session):
        super().__init__(session, Supplier)

    def get_by_code(
        self,
        code: str,
        organization_id: str | None = None,
    ) -> Supplier | None:
        statement = select(Supplier).where(Supplier.code == code)

        if organization_id is not None:
            statement = statement.where(
                Supplier.organization_id == organization_id
            )

        return self.session.scalar(statement)

    def get_by_organization(
        self,
        organization_id: str,
    ) -> list[Supplier]:
        return list(
            self.session.scalars(
                select(Supplier).where(
                    Supplier.organization_id == organization_id
                )
            ).all()
        )

    def get_by_id_for_organization(
        self,
        supplier_id: str,
        organization_id: str,
    ) -> Supplier | None:
        return self.session.scalar(
            select(Supplier).where(
                Supplier.id == supplier_id,
                Supplier.organization_id == organization_id,
            )
        )
