from pydantic import BaseModel


class MeterIn(BaseModel):
    name: str


class Meter(MeterIn):
    meter_id: str


class ReadingIn(BaseModel):
    meter_id: str
    value: float


class Reading(ReadingIn):
    reading_id: str


class MeterWithReadings(BaseModel):
    meter: Meter
    readings: list[Reading]
