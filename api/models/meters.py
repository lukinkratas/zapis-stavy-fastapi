import datetime
import uuid

from pydantic import BaseModel

from .readings import ReadingResponseJson


class MeterCreateRequestBody(BaseModel):
    """Meter request body model for validation."""

    name: str
    description: str | None = None


class MeterUpdateRequestBody(BaseModel):
    """Meter request body model for validation."""

    name: str | None = None
    description: str | None = None


class MeterResponseJson(BaseModel):
    """Meter response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    name: str
    description: str | None


class MeterWithReadingsResponseJson(BaseModel):
    """Meter and its' corresponsing readings response json model for validation."""

    meter: MeterResponseJson
    readings: list[ReadingResponseJson]
