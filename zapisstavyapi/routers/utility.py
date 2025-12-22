import uuid
from typing import Any, NoReturn, TypeAlias

from fastapi import APIRouter, HTTPException

from zapisstavyapi.models.utility import (
    Meter,
    MeterIn,
    MeterWithReadings,
    Reading,
    ReadingIn,
)

router = APIRouter()

MeterDict: TypeAlias = dict[str, str]
ReadingDict: TypeAlias = dict[str, Any]
MeterWithReadingsDict: TypeAlias = dict[str, Any]

meters_table: dict[str, MeterDict] = {}
readings_table: dict[str, ReadingDict] = {}


@router.post('/meter', response_model=Meter, status_code=201)
async def create_meter(meter_in: MeterIn) -> MeterDict:
    """Add new meter into the database.

    Args:
        meter_in: meter dict input from client

    Returns: meter dict
    """
    meter_id = str(uuid.uuid4())
    new_meter = {**meter_in.model_dump(), 'meter_id': meter_id}
    meters_table[meter_id] = new_meter
    return new_meter


@router.get('/meter', response_model=list[Meter])
async def get_all_meters() -> list[MeterDict]:
    """List all meter dicts in the database.

    Returns: list of meter dicts
    """
    return list(meters_table.values())


@router.post('/reading', response_model=Reading, status_code=201)
async def create_reading(reading_in: ReadingIn) -> ReadingDict | NoReturn:
    """Add new reading into the database.

    Args:
        reading_in: reading dict input from client

    Returns: reading dict

    Raises:
        HTTPException:
            If meter with given meter_id (in reading_in) is not found in the database.
    """
    if reading_in.meter_id not in meters_table:
        raise HTTPException(status_code=404, detail='Meter not found')

    reading_id = str(uuid.uuid4())
    new_reading = {**reading_in.model_dump(), 'reading_id': reading_id}
    readings_table[reading_id] = new_reading
    return new_reading


@router.get('/meter/{meter_id}/reading', response_model=list[Reading])
async def get_readings_on_meter(meter_id: str) -> list[ReadingDict]:
    """List all readings on a given meter.

    Args:
        meter_id: uuid of meter

    Returns:
        list of reading dicts
    """
    return [
        reading
        for reading in readings_table.values()
        if reading['meter_id'] == meter_id
    ]


@router.get('/meter/{meter_id}', response_model=MeterWithReadings)
async def get_meter_with_readings(meter_id: str) -> MeterWithReadingsDict | NoReturn:
    """List all reading on a given meter.

    Args:
        meter_id: uuid of meter

    Returns:
        dict with meter dict and list of corresponding reading dicts together

    Raises:
        HTTPException: If meter with given meter_id is not found in the database.
    """
    meter = meters_table.get(meter_id)

    if not meter:
        raise HTTPException(status_code=404, detail='Meter not found')

    return {'meter': meter, 'readings': await get_readings_on_meter(meter_id)}
