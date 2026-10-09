from backend.decision_engine.models import Decision


def evaluate_inventory(
    current_inventory: float,
    reorder_point: float,
    stockout_risk: str,
) -> Decision | None:

    if stockout_risk == "critical":
        return Decision(
            action="REORDER_IMMEDIATELY",
            priority="critical",
            reason="Inventory is at or below zero.",
            confidence=98.0,
            category="inventory",
        )

    if stockout_risk == "high":
        return Decision(
            action="REORDER_NOW",
            priority="high",
            reason="Inventory is below the calculated reorder point.",
            confidence=95.0,
            category="inventory",
        )

    if stockout_risk == "medium":
        return Decision(
            action="MONITOR_INVENTORY",
            priority="medium",
            reason="Inventory is approaching the reorder point.",
            confidence=85.0,
            category="inventory",
        )

    return None


def evaluate_supplier(
    supplier_risk_level: str,
) -> Decision | None:

    if supplier_risk_level == "critical":
        return Decision(
            action="REVIEW_SUPPLIER_IMMEDIATELY",
            priority="critical",
            reason="Supplier performance is critically weak.",
            confidence=95.0,
            category="supplier",
        )

    if supplier_risk_level == "high":
        return Decision(
            action="CONSIDER_BACKUP_SUPPLIER",
            priority="high",
            reason="Supplier performance presents significant risk.",
            confidence=90.0,
            category="supplier",
        )

    if supplier_risk_level == "medium":
        return Decision(
            action="MONITOR_SUPPLIER",
            priority="medium",
            reason="Supplier performance requires monitoring.",
            confidence=80.0,
            category="supplier",
        )

    return None


def evaluate_overstock(
    overstock_risk: str,
) -> Decision | None:

    if overstock_risk == "high":
        return Decision(
            action="REDUCE_REORDER_QUANTITY",
            priority="high",
            reason="Inventory level indicates significant overstock risk.",
            confidence=90.0,
            category="inventory",
        )

    if overstock_risk == "medium":
        return Decision(
            action="REVIEW_REORDER_QUANTITY",
            priority="medium",
            reason="Inventory is above the preferred operating range.",
            confidence=80.0,
            category="inventory",
        )

    return None
