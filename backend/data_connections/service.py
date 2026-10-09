from __future__ import annotations

from datetime import datetime
from typing import Any

import backend.connectors.bootstrap

from sqlalchemy.orm import Session

from backend.connectors import ConnectorRegistry
from backend.database.models import DataConnection
from backend.database.repositories import DataConnectionRepository
from backend.secrets import SecretStore


class DataConnectionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = DataConnectionRepository(db)

    def list(
        self,
        organization_id: str,
    ) -> list[DataConnection]:
        return self.repo.get_by_organization(
            organization_id
        )

    def get(
        self,
        organization_id: str,
        connection_id: str,
    ) -> DataConnection | None:
        return self.repo.get_for_organization(
            organization_id,
            connection_id,
        )

    def create(
        self,
        organization_id: str,
        name: str,
        connector_type: str,
        config: dict[str, Any],
        secrets: dict[str, str] | None = None,
        description: str | None = None,
    ) -> DataConnection:

        connector_type = connector_type.lower().strip()

        if connector_type not in ConnectorRegistry.available():
            raise ValueError(
                f"Unsupported connector type: {connector_type}"
            )

        if not name.strip():
            raise ValueError(
                "Connection name cannot be empty."
            )

        encrypted_secrets = {
            key: SecretStore.encrypt(str(value))
            for key, value in (secrets or {}).items()
            if value is not None
        }

        connection = DataConnection(
            organization_id=organization_id,
            name=name.strip(),
            connector_type=connector_type,
            description=description,
            config=config,
            secret_config=encrypted_secrets,
            status="configured",
            enabled=True,
        )

        return self.repo.add(connection)

    def _connector_config(
        self,
        connection: DataConnection,
    ) -> dict[str, Any]:

        config = dict(connection.config or {})

        for key, encrypted_value in (
            connection.secret_config or {}
        ).items():

            config[key] = SecretStore.decrypt(
                encrypted_value
            )

        return config

    def _connector(
        self,
        connection: DataConnection,
    ):
        return ConnectorRegistry.create(
            connection.connector_type,
            self._connector_config(connection),
        )

    def test(
        self,
        organization_id: str,
        connection_id: str,
    ):
        connection = self.get(
            organization_id,
            connection_id,
        )

        if connection is None:
            return None

        connector = self._connector(connection)

        try:
            result = connector.test_connection()

            connection.status = (
                "healthy"
                if result.success
                else "error"
            )

            connection.last_tested_at = (
                datetime.utcnow()
            )

            self.db.commit()

            return result

        finally:
            connector.close()

    def preview(
        self,
        organization_id: str,
        connection_id: str,
        limit: int = 100,
    ):
        connection = self.get(
            organization_id,
            connection_id,
        )

        if connection is None:
            return None

        connector = self._connector(connection)

        try:
            return connector.preview(limit)

        finally:
            connector.close()

    def refresh(
        self,
        organization_id: str,
        connection_id: str,
    ) -> int:
        connection = self.get(
            organization_id,
            connection_id,
        )

        if connection is None:
            return 0

        connector = self._connector(connection)

        try:
            records = connector.read()

            connection.status = "healthy"
            connection.last_refreshed_at = (
                datetime.utcnow()
            )

            self.db.commit()

            return len(records)

        finally:
            connector.close()
