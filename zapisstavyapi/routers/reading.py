from fastapi import APIRouter

from zapisstavyapi.models.reading import Reading, ReadingIn

router = APIRouter()
readings = {}

@router.post('/reading', response_model=Reading, status_code=201)
async def create_reading(reading: ReadingIn) -> dict[str, str]:
    data = reading.model_dump()
    last_reading_id = len(readings)
    new_reading = {**data, 'sensor_id': last_reading_id}
    readings[last_reading_id] = new_reading
    return new_reading

@router.get('/reading', response_model=list[Reading])
async def get_all_readings():
    return list(readings.values())
