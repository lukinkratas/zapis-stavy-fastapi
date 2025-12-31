import uuid
from typing import Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from .db import db_connect
from .db_models import MetersTable, ReadingsTable
from .models import MeterReq, MeterResp, MeterWithReadingsResp, ReadingReq, ReadingResp

router = APIRouter()


@router.post("/meter", status_code=201, response_model=MeterResp)
async def create_meter(
    meter_request: MeterReq, db_connection: Connection = Depends(db_connect)
) -> MeterResp:
    """Add new meter into the database.

    Args:
        meter: meter dict input from client

    Returns: meter dict
    """
    return await MetersTable.create(db_connection, meter_request)


@router.get("/meter", response_model=list[MeterResp])
async def get_all_meters(
    db_connection: Connection = Depends(db_connect),
) -> list[MeterResp]:
    """List all meter dicts in the database.

    Returns: list of meter dicts
    """
    return await MetersTable.retrieve_all(db_connection)


@router.post("/reading", status_code=201, response_model=ReadingResp)
async def create_reading(
    reading_request: ReadingReq, db_connection: Connection = Depends(db_connect)
) -> ReadingResp:
    """Add new reading into the database.

    Args:
        reading: reading dict input from client

    Returns: reading dict

    Raises:
        HTTPException:
            If meter with given meter_id (in reading_in) is not found in the database.
    """
    return await ReadingsTable.create(db_connection, reading_request)


@router.get("/meter/{meter_id}/reading", response_model=list[ReadingResp])
async def get_readings_on_meter(
    meter_id: uuid.UUID, db_connection: Connection = Depends(db_connect)
) -> list[ReadingResp]:
    """List all readings on a given meter.

    Args:
        meter_id: uuid of meter

    Returns:
        list of reading dicts
    """
    return await ReadingsTable.retrieve_by_meter_id(db_connection, meter_id)


@router.get("/meter/{meter_id}", response_model=MeterWithReadingsResp)
async def get_meter_with_readings(
    meter_id: uuid.UUID, db_connection: Connection = Depends(db_connect)
) -> dict[str, Any]:
    """List a given meter and all corresponding readings.

    Args:
        meter_id: uuid of meter

    Returns:
        dict with meter dict and list of corresponding reading dicts together

    Raises:
        HTTPException: If meter with given meter_id is not found in the database.
    """
    return {
        "meter": await MetersTable.retrieve_by_id(db_connection, meter_id),
        "readings": await ReadingsTable.retrieve_by_meter_id(db_connection, meter_id),
    }
