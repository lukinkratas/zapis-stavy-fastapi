import datetime
import uuid

from pydantic import BaseModel


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


class ReadingCreateRequestBody(BaseModel):
    """Reading request body model for validation."""

    meter_id: uuid.UUID
    value: float | None = None


class ReadingUpdateRequestBody(BaseModel):
    """Reading request body model for validation."""

    value: float


class ReadingResponseJson(BaseModel):
    """Reading response json model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime
    meter_id: uuid.UUID
    value: float


class MeterWithReadingsResponseJson(BaseModel):
    """Meter and its' corresponsing readings response json model for validation."""

    meter: MeterResponseJson
    readings: list[ReadingResponseJson]
