from __future__ import annotations

from pathlib import Path
from typing import Iterable

from backend.data_ingestion.models import IngestionResult
from backend.data_ingestion.parsers.csv_parser import CSVParser
from backend.data_ingestion.validators.quality import (
    DataQualityValidator,
)


class DataIngestionService:
    """Coordinate parsing and validation of incoming data."""

    @staticmethod
    def ingest_csv(
        file_path: str | Path,
        required_columns: Iterable[str] | None = None,
    ) -> IngestionResult:
        source = str(file_path)

        try:
            records = CSVParser.parse(file_path)
        except (FileNotFoundError, ValueError) as exc:
            from backend.data_ingestion.models import DataQualityResult

            quality = DataQualityResult(
                valid=False,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                missing_values=0,
                duplicate_rows=0,
                errors=[str(exc)],
            )

            return IngestionResult(
                success=False,
                source=source,
                records_processed=0,
                records_accepted=0,
                records_rejected=0,
                quality=quality,
            )

        quality = DataQualityValidator.validate(
            records,
            required_columns,
        )

        accepted = [
            record
            for record in records
            if all(
                record.get(column) not in (None, "")
                for column in (required_columns or [])
            )
        ]

        return IngestionResult(
            success=quality.valid,
            source=source,
            records_processed=len(records),
            records_accepted=len(accepted),
            records_rejected=len(records) - len(accepted),
            quality=quality,
            data=accepted,
        )
