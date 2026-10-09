from sqlalchemy.orm import Session

from backend.database.models import Product
from backend.database.repositories import ProductRepository


class ProductService:
    def __init__(self, session: Session):
        self.repository = ProductRepository(session)

    def create(
        self,
        organization_id: str,
        sku: str,
        name: str,
        category: str | None = None,
        unit_cost: float = 0.0,
        selling_price: float = 0.0,
        lead_time_days: int = 7,
    ) -> Product:
        sku = sku.strip()
        name = name.strip()

        if not sku:
            raise ValueError("SKU cannot be empty")

        if not name:
            raise ValueError("Product name cannot be empty")

        if unit_cost < 0:
            raise ValueError("Unit cost cannot be negative")

        if selling_price < 0:
            raise ValueError("Selling price cannot be negative")

        if lead_time_days < 0:
            raise ValueError("Lead time cannot be negative")

        if self.repository.get_by_sku(sku):
            raise ValueError(f"Product with SKU '{sku}' already exists")

        product = Product(
            organization_id=organization_id,
            sku=sku,
            name=name,
            category=category,
            unit_cost=unit_cost,
            selling_price=selling_price,
            lead_time_days=lead_time_days,
        )

        return self.repository.add(product)

    def get(self, product_id: str) -> Product | None:
        return self.repository.get_by_id(product_id)

    def list(self, organization_id: str) -> list[Product]:
        return self.repository.get_by_organization(organization_id)

    def list_active(self, organization_id: str) -> list[Product]:
        return self.repository.get_active(organization_id)
