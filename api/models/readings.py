import datetime
import uuid

from pydantic import BaseModel


class ReadingCreateRequestBody(BaseModel):
    """Reading create request body model for validation."""

    meter_id: uuid.UUID
    value: float | None = None


class ReadingUpdateRequestBody(BaseModel):
    """Reading update request body model for validation."""

    value: float


class ReadingResponseJson(BaseModel):
    """Reading response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    meter_id: uuid.UUID
    value: float
