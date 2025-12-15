from fastapi import FastAPI
from zapisstavyapi.models.reading import Reading, ReadingIn

app = FastAPI()

readings = {}

@app.post('/reading', response_model=Reading)
async def create_reading(reading: ReadingIn) -> dict[str, str]:
    data = reading.dict()
    last_reading_id = len(readings)
    new_reading = {**data, 'sensor_id': last_reading_id}
    readings[last_reading_id] = new_reading
    return new_reading

@app.get('/reading', response_model=list[Reading])
async def get_all_readings():
    return list(readings.values())
