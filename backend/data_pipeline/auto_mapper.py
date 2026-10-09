from __future__ import annotations

import re


FIELD_ALIASES = {
    "demand_date": [
        "date",
        "demand_date",
        "order_date",
        "transaction_date",
        "sales_date",
    ],
    "inventory_date": [
        "date",
        "inventory_date",
        "stock_date",
    ],
    "bullwhip_date": [
        "date",
        "period",
        "bullwhip_date",
        "order_date",
        "transaction_date",
    ],
    "product_sku": [
        "sku",
        "product_sku",
        "product_code",
        "item_code",
        "stock_code",
    ],
    "product_name": [
        "product",
        "product_name",
        "item",
        "item_name",
        "product_description",
    ],
    "category": [
        "category",
        "product_category",
        "type",
        "segment",
    ],
    "quantity": [
        "quantity",
        "qty",
        "units",
        "volume",
        "demand",
        "sales_quantity",
    ],
    "revenue": [
        "revenue",
        "sales",
        "sales_amount",
        "total_sales",
        "amount",
    ],
    "unit_cost": [
        "unit_cost",
        "cost",
        "purchase_cost",
        "cost_per_unit",
    ],
    "selling_price": [
        "selling_price",
        "price",
        "sale_price",
        "unit_price",
    ],
    "lead_time_days": [
        "lead_time",
        "lead_time_days",
        "delivery_days",
        "shipping_days",
    ],
    "on_hand": [
        "on_hand",
        "stock",
        "inventory",
        "current_stock",
        "available_stock",
    ],
    "reserved": [
        "reserved",
        "reserved_stock",
        "allocated",
    ],
    "safety_stock": [
        "safety_stock",
    ],
    "reorder_point": [
        "reorder_point",
        "reorder_level",
        "rop",
    ],
    "stockout": [
        "stockout",
        "stock_out",
        "out_of_stock",
    ],
    "supplier_name": [
        "supplier",
        "supplier_name",
        "vendor",
        "vendor_name",
    ],
    "customer_demand": [
        "customer_demand",
        "customer_demand_qty",
        "customer_orders",
    ],
    "retailer_orders": [
        "retailer_orders",
        "retailer_order",
        "retailer_demand",
    ],
    "distributor_orders": [
        "distributor_orders",
        "distributor_order",
        "distributor_demand",
    ],
    "manufacturer_orders": [
        "manufacturer_orders",
        "manufacturer_order",
        "manufacturer_demand",
    ],
}


def normalize_column(value: str) -> str:
    value = value.strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    return value.strip("_")


class AutoMapper:
    @staticmethod
    def suggest(
        columns: list[str],
        target: str,
    ) -> dict:

        normalized = {
            column: normalize_column(column)
            for column in columns
        }

        suggestions = {}
        used_targets = set()

        target_name = target.lower().strip()

        # Generic "date" is ambiguous. Resolve it from the
        # requested import target instead of relying on the
        # FIELD_ALIASES dictionary order.
        target_date_field = {
            "demand": "demand_date",
            "inventory": "inventory_date",
            "bullwhip": "bullwhip_date",
        }.get(target_name)

        for original, normalized_name in normalized.items():

            if normalized_name == "date" and target_date_field:
                suggestions[original] = {
                    "target": target_date_field,
                    "confidence": 100,
                }
                used_targets.add(target_date_field)
                continue

            best_target = None
            best_score = 0

            for field, aliases in FIELD_ALIASES.items():

                for alias in aliases:

                    alias_normalized = normalize_column(alias)

                    score = 0

                    if normalized_name == alias_normalized:
                        score = 100

                    elif (
                        normalized_name in alias_normalized
                        or alias_normalized in normalized_name
                    ):
                        score = 80

                    elif (
                        normalized_name.replace("_", "")
                        == alias_normalized.replace("_", "")
                    ):
                        score = 90

                    if score > best_score:
                        best_score = score
                        best_target = field

            if (
                best_target
                and best_score >= 80
                and best_target not in used_targets
            ):
                suggestions[original] = {
                    "target": best_target,
                    "confidence": best_score,
                }

                used_targets.add(best_target)

        required_by_target = {
            "products": [
                "product_sku",
                "product_name",
            ],
            "demand": [
                "demand_date",
                "product_sku",
                "quantity",
            ],
            "inventory": [
                "inventory_date",
                "product_sku",
                "on_hand",
            ],
            "suppliers": [
                "supplier_name",
            ],
            "bullwhip": [
                "bullwhip_date",
                "customer_demand",
                "retailer_orders",
                "distributor_orders",
                "manufacturer_orders",
            ],
        }

        required = required_by_target.get(
            target_name,
            [],
        )

        mapped_targets = {
            value["target"]
            for value in suggestions.values()
        }

        missing_required = [
            field
            for field in required
            if field not in mapped_targets
        ]

        return {
            "target": target,
            "columns": columns,
            "suggestions": suggestions,
            "missing_required": missing_required,
            "ready": not missing_required,
        }

