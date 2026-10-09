from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import uuid4

import pandas as pd
from sqlalchemy.orm import Session

from backend.database.models import (
    DemandRecord,
    InventoryRecord,
    Product,
    Supplier,
)


class CanonicalImportService:

    SHEET_TARGETS = {
        "suppliers": "suppliers",
        "products": "products",
        "demand": "demand",
        "inventory": "inventory",
    }

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _clean(value):
        if pd.isna(value):
            return None
        return value

    @staticmethod
    def _text(value):
        value = CanonicalImportService._clean(value)
        if value is None:
            return None
        return str(value).strip()

    @staticmethod
    def _float(value, default=0.0):
        value = CanonicalImportService._clean(value)
        if value is None:
            return default
        return float(value)

    @staticmethod
    def _int(value, default=0):
        value = CanonicalImportService._clean(value)
        if value is None:
            return default
        return int(float(value))

    @staticmethod
    def _date(value):
        value = CanonicalImportService._clean(value)

        if value is None:
            return None

        if isinstance(value, pd.Timestamp):
            return value.date()

        if isinstance(value, date):
            return value

        return pd.to_datetime(value).date()

    def _read_sheet(
        self,
        path: str,
        sheet_name: str,
    ) -> pd.DataFrame:

        file_path = Path(path)

        if not file_path.exists():
            raise ValueError(
                f"Uploaded source file not found: {file_path}"
            )

        suffix = file_path.suffix.lower()

        if suffix == ".xlsx":
            return pd.read_excel(
                file_path,
                sheet_name=sheet_name,
            )

        if suffix == ".csv":
            return pd.read_csv(file_path)

        if suffix == ".json":
            return pd.read_json(file_path)

        raise ValueError(
            f"Unsupported source format: {suffix}"
        )

    def list_sheets(self, path: str) -> list[str]:

        file_path = Path(path)

        if file_path.suffix.lower() != ".xlsx":
            return ["default"]

        return list(
            pd.ExcelFile(file_path).sheet_names
        )

    def import_suppliers(
        self,
        organization_id: str,
        path: str,
        sheet_name: str = "suppliers",
    ):

        df = self._read_sheet(
            path,
            sheet_name,
        )

        imported = 0
        errors = []

        for index, row in df.iterrows():

            try:
                code = self._text(
                    row.get("supplier_code")
                )

                name = self._text(
                    row.get("name")
                )

                if not code or not name:
                    raise ValueError(
                        "supplier_code and name are required"
                    )

                supplier = (
                    self.db.query(Supplier)
                    .filter(
                        Supplier.organization_id
                        == organization_id,
                        Supplier.code == code,
                    )
                    .first()
                )

                if supplier is None:
                    supplier = Supplier(
                        id=str(uuid4()),
                        organization_id=organization_id,
                        code=code,
                        name=name,
                        lead_time_days=self._int(
                            row.get("lead_time_days")
                        ),
                        reliability_score=self._float(
                            row.get("reliability_score"),
                            0.0,
                        ),
                    )
                    self.db.add(supplier)

                else:
                    supplier.name = name
                    supplier.lead_time_days = self._int(
                        row.get("lead_time_days"),
                        supplier.lead_time_days or 0,
                    )
                    supplier.reliability_score = self._float(
                        row.get("reliability_score"),
                        supplier.reliability_score or 0.0,
                    )

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index + 2,
                    "message": str(exc),
                })

        self.db.flush()

        return imported, errors

    def _supplier(
        self,
        organization_id: str,
        supplier_code: str | None,
    ):

        if not supplier_code:
            return None

        return (
            self.db.query(Supplier)
            .filter(
                Supplier.organization_id
                == organization_id,
                Supplier.code == supplier_code,
            )
            .first()
        )

    def _product(
        self,
        organization_id: str,
        sku: str,
    ):

        return (
            self.db.query(Product)
            .filter(
                Product.organization_id
                == organization_id,
                Product.sku == sku,
            )
            .first()
        )

    def import_products(
        self,
        organization_id: str,
        path: str,
        sheet_name: str = "products",
    ):

        df = self._read_sheet(
            path,
            sheet_name,
        )

        imported = 0
        errors = []

        for index, row in df.iterrows():

            try:
                sku = self._text(
                    row.get("sku")
                )

                name = self._text(
                    row.get("name")
                )

                if not sku or not name:
                    raise ValueError(
                        "sku and name are required"
                    )

                supplier_code = self._text(
                    row.get("supplier_code")
                )

                supplier = self._supplier(
                    organization_id,
                    supplier_code,
                )

                product = self._product(
                    organization_id,
                    sku,
                )

                if product is None:
                    product = Product(
                        id=str(uuid4()),
                        organization_id=organization_id,
                        supplier_id=(
                            supplier.id
                            if supplier
                            else None
                        ),
                        sku=sku,
                        name=name,
                        category=self._text(
                            row.get("category")
                        ),
                        unit_cost=self._float(
                            row.get("unit_cost")
                        ),
                        selling_price=self._float(
                            row.get("selling_price")
                        ),
                        lead_time_days=self._int(
                            row.get("lead_time_days")
                        ),
                        active=True,
                    )

                    self.db.add(product)

                else:
                    product.name = name
                    product.category = self._text(
                        row.get("category")
                    )
                    product.unit_cost = self._float(
                        row.get("unit_cost"),
                        product.unit_cost or 0.0,
                    )
                    product.selling_price = self._float(
                        row.get("selling_price"),
                        product.selling_price or 0.0,
                    )
                    product.lead_time_days = self._int(
                        row.get("lead_time_days"),
                        product.lead_time_days or 0,
                    )
                    product.active = True

                    if supplier:
                        product.supplier_id = supplier.id

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index + 2,
                    "message": str(exc),
                })

        self.db.flush()

        return imported, errors

    def import_demand(
        self,
        organization_id: str,
        path: str,
        sheet_name: str = "demand",
    ):

        df = self._read_sheet(
            path,
            sheet_name,
        )

        imported = 0
        errors = []

        for index, row in df.iterrows():

            try:
                sku = self._text(
                    row.get("sku")
                )

                record_date = self._date(
                    row.get("date")
                )

                quantity = self._float(
                    row.get("quantity")
                )

                if not sku or record_date is None:
                    raise ValueError(
                        "sku and date are required"
                    )

                product = self._product(
                    organization_id,
                    sku,
                )

                if product is None:
                    raise ValueError(
                        f"Product not found for SKU: {sku}"
                    )

                record = (
                    self.db.query(DemandRecord)
                    .filter(
                        DemandRecord.product_id
                        == product.id,
                        DemandRecord.date
                        == record_date,
                    )
                    .first()
                )

                revenue = self._float(
                    row.get("revenue")
                )

                if record is None:
                    record = DemandRecord(
                        id=str(uuid4()),
                        product_id=product.id,
                        date=record_date,
                        quantity=quantity,
                        revenue=revenue,
                    )
                    self.db.add(record)

                else:
                    record.quantity = quantity
                    record.revenue = revenue

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index + 2,
                    "message": str(exc),
                })

        self.db.flush()

        return imported, errors

    def import_inventory(
        self,
        organization_id: str,
        path: str,
        sheet_name: str = "inventory",
    ):

        df = self._read_sheet(
            path,
            sheet_name,
        )

        imported = 0
        errors = []

        for index, row in df.iterrows():

            try:
                sku = self._text(
                    row.get("sku")
                )

                record_date = self._date(
                    row.get("date")
                )

                if not sku or record_date is None:
                    raise ValueError(
                        "sku and date are required"
                    )

                product = self._product(
                    organization_id,
                    sku,
                )

                if product is None:
                    raise ValueError(
                        f"Product not found for SKU: {sku}"
                    )

                record = (
                    self.db.query(InventoryRecord)
                    .filter(
                        InventoryRecord.product_id
                        == product.id,
                        InventoryRecord.date
                        == record_date,
                    )
                    .first()
                )

                values = {
                    "on_hand": self._float(
                        row.get("on_hand")
                    ),
                    "reserved": self._float(
                        row.get("reserved")
                    ),
                    "safety_stock": self._float(
                        row.get("safety_stock")
                    ),
                    "reorder_point": self._float(
                        row.get("reorder_point")
                    ),
                    "stockout": bool(
                        row.get("stockout", False)
                    ),
                }

                if record is None:
                    record = InventoryRecord(
                        id=str(uuid4()),
                        product_id=product.id,
                        date=record_date,
                        **values,
                    )
                    self.db.add(record)

                else:
                    for key, value in values.items():
                        setattr(record, key, value)

                imported += 1

            except Exception as exc:
                errors.append({
                    "row": index + 2,
                    "message": str(exc),
                })

        self.db.flush()

        return imported, errors
