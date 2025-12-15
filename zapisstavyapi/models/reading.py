from pydantic import BaseModel

class ReadingIn(BaseModel):
    value: float

class Reading(ReadingIn):
    sensor_id: int