import datetime
import uuid

from pydantic import BaseModel


class MeterReq(BaseModel):
    name: str


class MeterResp(MeterReq):
    id: uuid.UUID
    created_at: datetime.datetime


class ReadingReq(BaseModel):
    meter_id: uuid.UUID
    value: float


class ReadingResp(ReadingReq):
    id: uuid.UUID
    created_at: datetime.datetime


class MeterWithReadingsResp(BaseModel):
    meter: MeterResp
    readings: list[ReadingResp]
