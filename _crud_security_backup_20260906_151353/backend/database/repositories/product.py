from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.product import Product
from backend.database.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Session):
        super().__init__(session, Product)

    def get_by_sku(
        self,
        sku: str,
        organization_id: str | None = None,
    ) -> Product | None:
        statement = select(Product).where(Product.sku == sku)

        if organization_id is not None:
            statement = statement.where(
                Product.organization_id == organization_id
            )

        return self.session.scalar(statement)

    def get_by_organization(
        self,
        organization_id: str,
    ) -> list[Product]:
        return list(
            self.session.scalars(
                select(Product).where(
                    Product.organization_id == organization_id
                )
            ).all()
        )

    def get_active(
        self,
        organization_id: str,
    ) -> list[Product]:
        return list(
            self.session.scalars(
                select(Product).where(
                    Product.organization_id == organization_id,
                    Product.active.is_(True),
                )
            ).all()
        )

    def get_by_id_for_organization(
        self,
        product_id: str,
        organization_id: str,
    ) -> Product | None:
        return self.session.scalar(
            select(Product).where(
                Product.id == product_id,
                Product.organization_id == organization_id,
            )
        )
