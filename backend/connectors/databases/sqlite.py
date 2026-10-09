from __future__ import annotations

from typing import Any

from backend.connectors.databases.sql import SQLConnector


class SQLiteConnector(SQLConnector):
    connector_type = "sqlite"

    def __init__(self, config: dict[str, Any]):
        path = config.get("path")

        if not path:
            raise ValueError("SQLite connector requires 'path'.")

        super().__init__({
            **config,
            "url": f"sqlite:///{path}",
        })
