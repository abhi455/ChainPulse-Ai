from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.product import Product
from backend.database.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Session):
        super().__init__(session, Product)

    def get_by_sku(self, sku: str) -> Product | None:
        return self.session.scalar(
            select(Product).where(Product.sku == sku)
        )

    def get_by_organization(self, organization_id: str) -> list[Product]:
        return list(
            self.session.scalars(
                select(Product).where(Product.organization_id == organization_id)
            ).all()
        )

    def get_active(self, organization_id: str) -> list[Product]:
        return list(
            self.session.scalars(
                select(Product).where(
                    Product.organization_id == organization_id,
                    Product.active.is_(True),
                )
            ).all()
        )
