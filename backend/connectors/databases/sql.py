from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, inspect, text

from backend.connectors.base import (
    BaseConnector,
    ConnectionResult,
    DataPreview,
)


class SQLConnector(BaseConnector):

    connector_type = "sql"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

        url = config.get("url")

        if not url:
            raise ValueError(
                "SQL connector requires 'url'."
            )

        self.engine = create_engine(
            url,
            pool_pre_ping=True,
        )

    def test_connection(self) -> ConnectionResult:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            inspector = inspect(self.engine)

            return ConnectionResult(
                True,
                "Database connection successful.",
                {
                    "dialect":
                        self.engine.dialect.name,
                    "tables":
                        inspector.get_table_names(),
                },
            )

        except Exception as exc:
            return ConnectionResult(
                False,
                str(exc),
            )

    def _query(self) -> str:
        query = self.config.get("query")

        if query:
            return query

        table = self.config.get("table")

        if not table:
            raise ValueError(
                "SQL connector requires 'query' or 'table'."
            )

        return f"SELECT * FROM {table}"

    def preview(self, limit: int = 100) -> DataPreview:
        query = self._query()

        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    f"SELECT * FROM ({query}) AS source_query LIMIT {limit}"
                )
            ).mappings().all()

            total = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM ({query}) AS count_query"
                )
            ).scalar_one()

        records = [dict(row) for row in rows]

        return DataPreview(
            columns=list(records[0].keys())
            if records
            else [],
            rows=records,
            total_rows=int(total),
            metadata={
                "dialect":
                    self.engine.dialect.name,
            },
        )

    def read(self) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(self._query())
            ).mappings().all()

        return [dict(row) for row in rows]

    def close(self) -> None:
        self.engine.dispose()
