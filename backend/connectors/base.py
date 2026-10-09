from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ConnectionResult:
    success: bool
    message: str
    metadata: dict[str, Any] | None = None


@dataclass
class DataPreview:
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int
    metadata: dict[str, Any] | None = None


class BaseConnector(ABC):

    connector_type: str = "base"

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    def test_connection(self) -> ConnectionResult:
        raise NotImplementedError

    @abstractmethod
    def preview(self, limit: int = 100) -> DataPreview:
        raise NotImplementedError

    @abstractmethod
    def read(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def close(self) -> None:
        return None
