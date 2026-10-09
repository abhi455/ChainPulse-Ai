from math import sqrt


class InventoryCalculator:

    @staticmethod
    def safety_stock(
        demand_std: float,
        lead_time_days: float,
        service_level_z: float = 1.65,
    ) -> float:
        if demand_std < 0:
            raise ValueError("demand_std cannot be negative")

        if lead_time_days < 0:
            raise ValueError("lead_time_days cannot be negative")

        if service_level_z <= 0:
            raise ValueError("service_level_z must be positive")

        return service_level_z * demand_std * sqrt(lead_time_days)

    @staticmethod
    def reorder_point(
        average_daily_demand: float,
        lead_time_days: float,
        safety_stock: float,
    ) -> float:
        if average_daily_demand < 0:
            raise ValueError(
                "average_daily_demand cannot be negative"
            )

        if lead_time_days < 0:
            raise ValueError("lead_time_days cannot be negative")

        if safety_stock < 0:
            raise ValueError("safety_stock cannot be negative")

        return (
            average_daily_demand * lead_time_days
            + safety_stock
        )

    @staticmethod
    def economic_order_quantity(
        annual_demand: float,
        ordering_cost: float,
        holding_cost: float,
    ) -> float:
        if annual_demand < 0:
            raise ValueError("annual_demand cannot be negative")

        if ordering_cost < 0:
            raise ValueError("ordering_cost cannot be negative")

        if holding_cost <= 0:
            raise ValueError("holding_cost must be positive")

        if annual_demand == 0 or ordering_cost == 0:
            return 0.0

        return sqrt(
            (2 * annual_demand * ordering_cost)
            / holding_cost
        )

    @staticmethod
    def days_of_inventory(
        current_inventory: float,
        average_daily_demand: float,
    ) -> float:
        if current_inventory < 0:
            raise ValueError(
                "current_inventory cannot be negative"
            )

        if average_daily_demand < 0:
            raise ValueError(
                "average_daily_demand cannot be negative"
            )

        if average_daily_demand == 0:
            return float("inf")

        return current_inventory / average_daily_demand
