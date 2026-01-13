import datetime
import uuid

from pydantic import BaseModel

from .readings import ReadingResponseJson


class MeterCreateRequestBody(BaseModel):
    """Meter create request body model for validation."""

    user_id: uuid.UUID
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


class MeterWithReadingsResponseJson(BaseModel):
    """Meter and its' corresponsing readings response json model for validation."""

    meter: MeterResponseJson
    readings: list[ReadingResponseJson]
