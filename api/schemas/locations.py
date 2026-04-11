import datetime
import uuid

from pydantic import BaseModel


class LocationCreateRequestBody(BaseModel):
    """Location create request body model for validation."""

    name: str


class LocationUpdateRequestBody(BaseModel):
    """Location update request body model for validation."""

    name: str | None = None


class LocationResponseJson(BaseModel):
    """Location response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    user_id: uuid.UUID
    name: str
