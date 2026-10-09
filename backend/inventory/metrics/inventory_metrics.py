def stockout_risk(
    current_inventory: float,
    reorder_point: float,
) -> str:
    if current_inventory < 0:
        raise ValueError(
            "current_inventory cannot be negative"
        )

    if reorder_point < 0:
        raise ValueError(
            "reorder_point cannot be negative"
        )

    if current_inventory <= 0:
        return "critical"

    if current_inventory < reorder_point:
        return "high"

    if current_inventory < reorder_point * 1.25:
        return "medium"

    return "low"


def overstock_risk(
    current_inventory: float,
    reorder_point: float,
    economic_order_quantity: float,
) -> str:
    if current_inventory < 0:
        raise ValueError(
            "current_inventory cannot be negative"
        )

    if reorder_point < 0:
        raise ValueError(
            "reorder_point cannot be negative"
        )

    if economic_order_quantity < 0:
        raise ValueError(
            "economic_order_quantity cannot be negative"
        )

    threshold = reorder_point + economic_order_quantity

    if current_inventory > threshold * 2:
        return "high"

    if current_inventory > threshold:
        return "medium"

    return "low"
