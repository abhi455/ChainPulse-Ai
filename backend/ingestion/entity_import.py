from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from backend.database.models import (
    BullwhipRecord,
    DemandRecord,
    InventoryRecord,
    Product,
    Supplier,
)
from backend.database.repositories import (
    DemandRepository,
    ProductRepository,
    SupplierRepository,
)


class EntityImportService:

    def __init__(self, db: Session):
        self.db = db

    def import_products(
        self,
        organization_id: str,
        rows: list[dict],
    ) -> tuple[int, list[dict]]:

        imported = 0
        errors = []

        for index, row in enumerate(rows, start=1):
            try:
                sku = str(row.get("sku", "")).strip()
                name = str(row.get("name", "")).strip()

                if not sku or not name:
                    raise ValueError(
                        "sku and name are required"
                    )

                product = self.db.query(Product).filter(
                    Product.organization_id == organization_id,
                    Product.sku == sku,
                ).first()

                if product is None:
                    product = Product(
                        organization_id=organization_id,
                        sku=sku,
                        name=name,
                        category=row.get("category"),
                        unit_cost=float(
                            row.get("unit_cost", 0) or 0
                        ),
                        selling_price=float(
                            row.get("selling_price", 0) or 0
                        ),
                        lead_time_days=int(
                            row.get("lead_time_days", 7) or 7
                        ),
                    )
                    self.db.add(product)
                else:
                    product.name = name
                    product.category = row.get(
                        "category"
                    )
                    product.unit_cost = float(
                        row.get("unit_cost", 0) or 0
                    )
                    product.selling_price = float(
                        row.get("selling_price", 0) or 0
                    )
                    product.lead_time_days = int(
                        row.get("lead_time_days", 7) or 7
                    )

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index,
                    "message": str(exc),
                })

        return imported, errors

    def import_demand(
        self,
        organization_id: str,
        rows: list[dict],
    ) -> tuple[int, list[dict]]:

        imported = 0
        errors = []

        for index, row in enumerate(rows, start=1):
            try:
                sku = str(
                    row.get("product_sku", "")
                ).strip()

                product = self.db.query(Product).filter(
                    Product.organization_id == organization_id,
                    Product.sku == sku,
                ).first()

                if product is None:
                    raise ValueError(
                        f"Product not found for SKU '{sku}'"
                    )

                demand_date = row.get(
                    "demand_date"
                )

                if isinstance(
                    demand_date,
                    str,
                ):
                    demand_date = date.fromisoformat(
                        demand_date[:10]
                    )

                quantity = float(
                    row.get("quantity", 0) or 0
                )

                revenue = float(
                    row.get("revenue", 0) or 0
                )

                existing = self.db.query(
                    DemandRecord
                ).filter(
                    DemandRecord.product_id
                    == product.id,
                    DemandRecord.date
                    == demand_date,
                ).first()

                if existing:
                    existing.quantity = quantity
                    existing.revenue = revenue
                else:
                    self.db.add(
                        DemandRecord(
                            product_id=product.id,
                            date=demand_date,
                            quantity=quantity,
                            revenue=revenue,
                        )
                    )

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index,
                    "message": str(exc),
                })

        return imported, errors

    def import_inventory(
        self,
        organization_id: str,
        rows: list[dict],
    ) -> tuple[int, list[dict]]:

        imported = 0
        errors = []

        for index, row in enumerate(rows, start=1):
            try:
                sku = str(
                    row.get("product_sku", "")
                ).strip()

                product = self.db.query(Product).filter(
                    Product.organization_id == organization_id,
                    Product.sku == sku,
                ).first()

                if product is None:
                    raise ValueError(
                        f"Product not found for SKU '{sku}'"
                    )

                record_date = row.get("inventory_date")

                if isinstance(
                    record_date,
                    str,
                ):
                    record_date = date.fromisoformat(
                        record_date[:10]
                    )

                on_hand = float(
                    row.get("on_hand", 0) or 0
                )

                reserved = float(
                    row.get("reserved", 0) or 0
                )

                safety_stock = float(
                    row.get("safety_stock", 0) or 0
                )

                reorder_point = float(
                    row.get("reorder_point", 0) or 0
                )

                stockout = bool(
                    row.get(
                        "stockout",
                        on_hand <= 0,
                    )
                )

                existing = self.db.query(
                    InventoryRecord
                ).filter(
                    InventoryRecord.product_id
                    == product.id,
                    InventoryRecord.date
                    == record_date,
                ).first()

                if existing:
                    existing.on_hand = on_hand
                    existing.reserved = reserved
                    existing.safety_stock = safety_stock
                    existing.reorder_point = reorder_point
                    existing.stockout = stockout
                else:
                    self.db.add(
                        InventoryRecord(
                            product_id=product.id,
                            date=record_date,
                            on_hand=on_hand,
                            reserved=reserved,
                            safety_stock=safety_stock,
                            reorder_point=reorder_point,
                            stockout=stockout,
                        )
                    )

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index,
                    "message": str(exc),
                })

        return imported, errors
    def import_bullwhip(
        self,
        organization_id: str,
        rows: list[dict],
    ) -> tuple[int, list[dict]]:

        imported = 0
        errors = []

        for index, row in enumerate(rows, start=1):
            try:
                record_date = (
                    row.get("bullwhip_date")
                    or row.get("period")
                    or row.get("date")
                )

                if isinstance(record_date, str):
                    record_date = date.fromisoformat(
                        record_date[:10]
                    )

                if record_date is None:
                    raise ValueError(
                        "bullwhip_date is required"
                    )

                customer_demand = float(
                    row.get("customer_demand")
                )

                retailer_orders = float(
                    row.get("retailer_orders")
                )

                distributor_orders = float(
                    row.get("distributor_orders")
                )

                manufacturer_orders = float(
                    row.get("manufacturer_orders")
                )

                values = {
                    "customer_demand": customer_demand,
                    "retailer_orders": retailer_orders,
                    "distributor_orders": distributor_orders,
                    "manufacturer_orders": manufacturer_orders,
                }

                for field, value in values.items():
                    if value < 0:
                        raise ValueError(
                            f"{field} cannot be negative"
                        )

                existing = self.db.query(
                    BullwhipRecord
                ).filter(
                    BullwhipRecord.organization_id
                    == organization_id,
                    BullwhipRecord.date
                    == record_date,
                ).first()

                if existing:
                    existing.customer_demand = customer_demand
                    existing.retailer_orders = retailer_orders
                    existing.distributor_orders = distributor_orders
                    existing.manufacturer_orders = manufacturer_orders

                else:
                    self.db.add(
                        BullwhipRecord(
                            organization_id=organization_id,
                            date=record_date,
                            customer_demand=customer_demand,
                            retailer_orders=retailer_orders,
                            distributor_orders=distributor_orders,
                            manufacturer_orders=manufacturer_orders,
                        )
                    )

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index,
                    "message": str(exc),
                })

        return imported, errors
