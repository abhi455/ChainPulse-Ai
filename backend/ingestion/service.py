from __future__ import annotations

from typing import Any

from backend.data_pipeline import (
    ColumnMapper,
    DataValidator,
)
from backend.data_connections import (
    DataConnectionService,
)


class IngestionService:

    def __init__(self, db):
        self.db = db
        self.connections = DataConnectionService(db)

    def read(
        self,
        organization_id: str,
        connection_id: str,
    ) -> list[dict[str, Any]]:

        connection = self.connections.get(
            organization_id,
            connection_id,
        )

        if connection is None:
            raise ValueError(
                "Data connection not found."
            )

        import backend.connectors.bootstrap

        from backend.connectors import (
            ConnectorRegistry,
        )

        connector = ConnectorRegistry.create(
            connection.connector_type,
            connection.config,
        )

        return connector.read()

    def preview(
        self,
        organization_id: str,
        connection_id: str,
        mapping: dict[str, str],
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        records = self.read(
            organization_id,
            connection_id,
        )

        return ColumnMapper.map_records(
            records[:limit],
            mapping,
        )

    def validate(
        self,
        organization_id: str,
        connection_id: str,
        mapping: dict[str, str],
        required_fields: list[str],
    ):

        mapped = self.preview(
            organization_id,
            connection_id,
            mapping,
            limit=100000,
        )

        return DataValidator.required_fields(
            mapped,
            required_fields,
        )

    def normalize(
        self,
        organization_id: str,
        connection_id: str,
        mapping: dict[str, str],
    ) -> list[dict[str, Any]]:

        records = self.read(
            organization_id,
            connection_id,
        )

        return ColumnMapper.map_records(
            records,
            mapping,
        )
