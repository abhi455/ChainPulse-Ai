from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    action: str
    priority: str
    reason: str
    confidence: float
    category: str

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("action cannot be empty")

        if not self.priority.strip():
            raise ValueError("priority cannot be empty")

        if not self.reason.strip():
            raise ValueError("reason cannot be empty")

        if not 0 <= self.confidence <= 100:
            raise ValueError(
                "confidence must be between 0 and 100"
            )

        if not self.category.strip():
            raise ValueError("category cannot be empty")
