from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from backend.connectors.base import (
    BaseConnector,
    ConnectionResult,
    DataPreview,
)


class CSVConnector(BaseConnector):

    connector_type = "csv"

    def _path(self) -> Path:
        return Path(self.config["path"])

    def test_connection(self) -> ConnectionResult:
        path = self._path()

        if not path.exists():
            return ConnectionResult(
                False,
                f"File not found: {path}",
            )

        if not path.is_file():
            return ConnectionResult(
                False,
                f"Not a file: {path}",
            )

        return ConnectionResult(
            True,
            "CSV file is accessible.",
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
            },
        )

    def _frame(self) -> pd.DataFrame:
        return pd.read_csv(self._path())

    def preview(self, limit: int = 100) -> DataPreview:
        df = self._frame()
        preview = df.head(limit)

        return DataPreview(
            columns=list(df.columns),
            rows=preview.to_dict("records"),
            total_rows=len(df),
            metadata={
                "source": str(self._path()),
                "format": "csv",
            },
        )

    def read(self) -> list[dict[str, Any]]:
        return self._frame().to_dict("records")


class ExcelConnector(BaseConnector):

    connector_type = "xlsx"

    def _path(self) -> Path:
        return Path(self.config["path"])

    def _sheet(self) -> str | int:
        return self.config.get("sheet", 0)

    def test_connection(self) -> ConnectionResult:
        path = self._path()

        if not path.exists():
            return ConnectionResult(
                False,
                f"File not found: {path}",
            )

        try:
            workbook = pd.ExcelFile(path)
            return ConnectionResult(
                True,
                "Excel workbook is accessible.",
                {
                    "path": str(path),
                    "sheets": workbook.sheet_names,
                },
            )
        except Exception as exc:
            return ConnectionResult(False, str(exc))

    def _frame(self) -> pd.DataFrame:
        return pd.read_excel(
            self._path(),
            sheet_name=self._sheet(),
        )

    def preview(self, limit: int = 100) -> DataPreview:
        df = self._frame()
        preview = df.head(limit)

        return DataPreview(
            columns=list(df.columns),
            rows=preview.to_dict("records"),
            total_rows=len(df),
            metadata={
                "source": str(self._path()),
                "format": "xlsx",
            },
        )

    def read(self) -> list[dict[str, Any]]:
        return self._frame().to_dict("records")


class JSONConnector(BaseConnector):

    connector_type = "json"

    def _path(self) -> Path:
        return Path(self.config["path"])

    def test_connection(self) -> ConnectionResult:
        if not self._path().exists():
            return ConnectionResult(
                False,
                f"File not found: {self._path()}",
            )

        try:
            self._load()
            return ConnectionResult(
                True,
                "JSON file is accessible.",
                {"path": str(self._path())},
            )
        except Exception as exc:
            return ConnectionResult(False, str(exc))

    def _load(self) -> list[dict[str, Any]]:
        with self._path().open(
            "r",
            encoding="utf-8",
        ) as handle:
            data = json.load(handle)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return [data]

        raise ValueError(
            "JSON source must contain an object or list."
        )

    def preview(self, limit: int = 100) -> DataPreview:
        rows = self._load()

        columns = sorted(
            {
                key
                for row in rows
                if isinstance(row, dict)
                for key in row
            }
        )

        return DataPreview(
            columns=columns,
            rows=rows[:limit],
            total_rows=len(rows),
            metadata={
                "source": str(self._path()),
                "format": "json",
            },
        )

    def read(self) -> list[dict[str, Any]]:
        return self._load()
