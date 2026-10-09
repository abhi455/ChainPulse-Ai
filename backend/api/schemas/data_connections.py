from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DataConnectionCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    connector_type: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str | None = None

    config: dict[str, Any] = Field(
        default_factory=dict
    )

    secrets: dict[str, str] = Field(
        default_factory=dict
    )


class DataConnectionResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    connector_type: str
    description: str | None
    status: str
    enabled: bool
    last_tested_at: datetime | None
    last_refreshed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DataConnectionPreviewResponse(BaseModel):
    connection_id: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total_rows: int
    metadata: dict[str, Any] | None = None


class DataConnectionTestResponse(BaseModel):
    connection_id: str
    success: bool
    message: str
    metadata: dict[str, Any] | None = None


class DataConnectionRefreshResponse(BaseModel):
    connection_id: str
    success: bool
    message: str
    rows: int
    refreshed_at: datetime | None
