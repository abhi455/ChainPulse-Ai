from typing import Any

from pydantic import BaseModel, Field


class PreviewImportRequest(BaseModel):
    connection_id: str
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
    )


class MappingRequest(BaseModel):
    connection_id: str
    mapping: dict[str, str]


class ValidationRequest(BaseModel):
    connection_id: str
    mapping: dict[str, str]
    required_fields: list[str] = []


class ImportRequest(BaseModel):
    connection_id: str
    mapping: dict[str, str]
    required_fields: list[str] = []
    target: str


class ImportResponse(BaseModel):
    success: bool
    target: str
    rows_received: int
    rows_imported: int
    errors: list[dict[str, Any]]
