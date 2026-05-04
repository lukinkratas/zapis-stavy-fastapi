import datetime
import uuid

from pydantic import BaseModel


class LocationCreateRequest(BaseModel):
    """Location create request model for validation."""

    name: str


class LocationUpdateRequest(BaseModel):
    """Location update request model for validation."""

    name: str | None = None


class LocationResponse(BaseModel):
    """Location response model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    user_id: uuid.UUID
    name: str
