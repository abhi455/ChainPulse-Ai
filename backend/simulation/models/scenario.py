from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    name: str
    demand_change_pct: float = 0.0
    lead_time_change_pct: float = 0.0
    inventory_change_pct: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Scenario name cannot be empty")

        if self.demand_change_pct < -100:
            raise ValueError(
                "demand_change_pct cannot be below -100"
            )

        if self.lead_time_change_pct < -100:
            raise ValueError(
                "lead_time_change_pct cannot be below -100"
            )

        if self.inventory_change_pct < -100:
            raise ValueError(
                "inventory_change_pct cannot be below -100"
            )

    @staticmethod
    def apply_percentage(
        value: float,
        change_pct: float,
    ) -> float:
        if value < 0:
            raise ValueError("value cannot be negative")

        return value * (1 + change_pct / 100)
