from pydantic import BaseModel, Field


class AutoMappingRequest(BaseModel):
    connection_id: str

    target: str = Field(
        min_length=1,
        max_length=50,
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
    )
