from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


class CSVParser:
    """Parse CSV files into normalized dictionaries."""

    @staticmethod
    def parse(
        file_path: str | Path,
    ) -> list[dict[str, Any]]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        if path.suffix.lower() != ".csv":
            raise ValueError(
                "Only CSV files are supported."
            )

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV file has no header row."
                )

            headers = [
                header.strip()
                for header in reader.fieldnames
                if header
            ]

            if not headers:
                raise ValueError(
                    "CSV file contains no valid columns."
                )

            records: list[dict[str, Any]] = []

            for row in reader:
                normalized = {
                    key.strip(): (
                        value.strip()
                        if isinstance(value, str)
                        else value
                    )
                    for key, value in row.items()
                    if key is not None
                }

                if any(
                    value not in ("", None)
                    for value in normalized.values()
                ):
                    records.append(normalized)

        return records
