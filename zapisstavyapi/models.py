import datetime
import uuid

from pydantic import BaseModel


class MeterReq(BaseModel):
    """Meter request model for validation."""

    name: str


class MeterResp(MeterReq):
    """Meter response model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime


class ReadingReq(BaseModel):
    """Reading request model for validation."""

    meter_id: uuid.UUID
    value: float


class ReadingResp(ReadingReq):
    """Reading response model for validation."""

    id: uuid.UUID
    created_at: datetime.datetime


class MeterWithReadingsResp(BaseModel):
    """Meter and its' corresponsing readings response model for validation."""

    meter: MeterResp
    readings: list[ReadingResp]
