from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationIssue:
    row: int
    field: str
    message: str
    value: Any


@dataclass
class ValidationResult:
    valid: bool
    valid_rows: list[dict[str, Any]]
    issues: list[ValidationIssue]


class DataValidator:

    @staticmethod
    def required_fields(
        records: list[dict[str, Any]],
        fields: list[str],
    ) -> ValidationResult:

        valid_rows = []
        issues = []

        for index, record in enumerate(records, start=1):
            row_valid = True

            for field in fields:
                value = record.get(field)

                if value is None or (
                    isinstance(value, str)
                    and not value.strip()
                ):
                    row_valid = False

                    issues.append(
                        ValidationIssue(
                            row=index,
                            field=field,
                            message="Required value is missing.",
                            value=value,
                        )
                    )

            if row_valid:
                valid_rows.append(record)

        return ValidationResult(
            valid=not issues,
            valid_rows=valid_rows,
            issues=issues,
        )
