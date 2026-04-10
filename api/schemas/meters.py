import datetime
import uuid

from pydantic import BaseModel

class MeterCreateRequestBody(BaseModel):
    """Meter create request body model for validation."""

    name: str


class MeterUpdateRequestBody(BaseModel):
    """Meter update request body model for validation."""

    name: str | None = None


class MeterResponseJson(BaseModel):
    """Meter response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    user_id: uuid.UUID
    name: str