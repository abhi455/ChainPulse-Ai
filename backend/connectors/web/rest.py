from __future__ import annotations

from typing import Any

import requests

from backend.connectors.base import (
    BaseConnector,
    ConnectionResult,
    DataPreview,
)


class RESTConnector(BaseConnector):

    connector_type = "rest"

    def _request(self) -> Any:
        response = requests.request(
            method=self.config.get("method", "GET"),
            url=self.config["url"],
            headers=self.config.get("headers", {}),
            params=self.config.get("params"),
            json=self.config.get("json_body"),
            timeout=self.config.get("timeout", 30),
        )

        response.raise_for_status()
        return response.json()

    @staticmethod
    def _normalize(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [
                item if isinstance(item, dict)
                else {"value": item}
                for item in data
            ]

        if isinstance(data, dict):
            records = data.get("data")

            if isinstance(records, list):
                return [
                    item if isinstance(item, dict)
                    else {"value": item}
                    for item in records
                ]

            return [data]

        return [{"value": data}]

    def test_connection(self) -> ConnectionResult:
        try:
            data = self._request()
            rows = self._normalize(data)

            return ConnectionResult(
                True,
                "REST API connection successful.",
                {
                    "row_count": len(rows),
                },
            )
        except Exception as exc:
            return ConnectionResult(
                False,
                str(exc),
            )

    def preview(self, limit: int = 100) -> DataPreview:
        rows = self._normalize(
            self._request()
        )

        columns = sorted(
            {
                key
                for row in rows
                for key in row
            }
        )

        return DataPreview(
            columns=columns,
            rows=rows[:limit],
            total_rows=len(rows),
            metadata={
                "source": self.config["url"],
                "format": "rest",
            },
        )

    def read(self) -> list[dict[str, Any]]:
        return self._normalize(
            self._request()
        )
