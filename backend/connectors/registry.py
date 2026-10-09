from __future__ import annotations

from typing import Type

from backend.connectors.base import BaseConnector


class ConnectorRegistry:

    _connectors: dict[str, Type[BaseConnector]] = {}

    @classmethod
    def register(
        cls,
        connector_type: str,
        connector_class: Type[BaseConnector],
    ) -> None:
        cls._connectors[connector_type] = connector_class

    @classmethod
    def create(
        cls,
        connector_type: str,
        config: dict,
    ) -> BaseConnector:

        connector = cls._connectors.get(
            connector_type.lower()
        )

        if connector is None:
            raise ValueError(
                f"Unsupported connector type: {connector_type}"
            )

        return connector(config)

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._connectors)
