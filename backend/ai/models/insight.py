from dataclasses import dataclass


@dataclass(frozen=True)
class AIInsight:
    title: str
    summary: str
    recommendation: str
    confidence: float
    category: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title cannot be empty")

        if not self.summary.strip():
            raise ValueError("summary cannot be empty")

        if not self.recommendation.strip():
            raise ValueError(
                "recommendation cannot be empty"
            )

        if not 0 <= self.confidence <= 100:
            raise ValueError(
                "confidence must be between 0 and 100"
            )

        if not self.category.strip():
            raise ValueError(
                "category cannot be empty"
            )
