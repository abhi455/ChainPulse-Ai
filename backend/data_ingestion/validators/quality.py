from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from backend.data_ingestion.models import DataQualityResult


class DataQualityValidator:
    """Validate tabular records before downstream processing."""

    @staticmethod
    def validate(
        records: Iterable[Mapping[str, Any]],
        required_columns: Iterable[str] | None = None,
    ) -> DataQualityResult:
        rows = [dict(record) for record in records]
        total_rows = len(rows)

        if total_rows == 0:
            return DataQualityResult(
                valid=False,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                missing_values=0,
                duplicate_rows=0,
                errors=["No records were provided."],
            )

        required = {
            column.strip()
            for column in (required_columns or [])
            if column and column.strip()
        }

        errors: list[str] = []
        warnings: list[str] = []

        columns = set(rows[0].keys())

        missing_columns = sorted(
            required - columns
        )

        if missing_columns:
            errors.append(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        missing_values = 0

        for row in rows:
            for column in required:
                value = row.get(column)

                if value is None or (
                    isinstance(value, str)
                    and not value.strip()
                ):
                    missing_values += 1

        duplicate_rows = (
            total_rows - len(
                {
                    tuple(
                        sorted(
                            row.items(),
                            key=lambda item: item[0],
                        )
                    )
                    for row in rows
                }
            )
        )

        if duplicate_rows:
            warnings.append(
                f"{duplicate_rows} duplicate row(s) detected."
            )

        invalid_rows = 0

        if required:
            invalid_rows = sum(
                1
                for row in rows
                if any(
                    row.get(column) in (None, "")
                    for column in required
                )
            )

        if missing_columns:
            invalid_rows = total_rows

        valid_rows = total_rows - invalid_rows

        if missing_values:
            warnings.append(
                f"{missing_values} missing required value(s) detected."
            )

        valid = (
            not errors
            and valid_rows > 0
        )

        return DataQualityResult(
            valid=valid,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            missing_values=missing_values,
            duplicate_rows=max(0, duplicate_rows),
            errors=errors,
            warnings=warnings,
        )
