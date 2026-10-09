from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DataQualityResult:
    valid: bool
    total_rows: int
    valid_rows: int
    invalid_rows: int
    missing_values: int
    duplicate_rows: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def quality_score(self) -> float:
        if self.total_rows == 0:
            return 0.0

        score = (
            self.valid_rows / self.total_rows
        ) * 100.0

        return round(
            max(0.0, min(100.0, score)),
            2,
        )


@dataclass(slots=True)
class IngestionResult:
    success: bool
    source: str
    records_processed: int
    records_accepted: int
    records_rejected: int
    quality: DataQualityResult
    data: list[dict[str, Any]] = field(
        default_factory=list
    )
