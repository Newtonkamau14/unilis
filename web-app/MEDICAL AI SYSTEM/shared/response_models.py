from datetime import datetime, UTC
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ResponseMetadata(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    service: Optional[str] = None

    processing_time_ms: Optional[float] = None


class APIResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    success: bool

    message: str

    data: Optional[Any] = None

    metadata: Optional[
        ResponseMetadata
    ] = None


class ErrorResponse(BaseModel):
    success: bool = False

    error: str

    details: Optional[Any] = None