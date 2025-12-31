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
    meter: MeterReq, conn: Connection = Depends(db_connect)
) -> MeterResp:
    """Add new meter into the database.

    Args:
        meter: meter request payload from client
        conn: database connection

    Returns: meter response dict
    """
    return await MetersTable.create(conn, meter)


@router.get("/meter", response_model=list[MeterResp])
async def get_all_meters(
    conn: Connection = Depends(db_connect),
) -> list[MeterResp]:
    """List all meter dicts in the database.

    Args:
        conn: database connection

    Returns: list of meter response dicts
    """
    return await MetersTable.retrieve_all(conn)


@router.post("/reading", status_code=201, response_model=ReadingResp)
async def create_reading(
    reading: ReadingReq, conn: Connection = Depends(db_connect)
) -> ReadingResp:
    """Add new reading into the database.

    Args:
        reading: reading request payload from client
        conn: database connection

    Returns: reading response dict
    """
    return await ReadingsTable.create(conn, reading)


@router.get("/meter/{meter_id}/reading", response_model=list[ReadingResp])
async def get_readings_on_meter(
    meter_id: uuid.UUID, conn: Connection = Depends(db_connect)
) -> list[ReadingResp]:
    """List all readings on a given meter.

    Args:
        meter_id: uuid of meter
        conn: database connection

    Returns: list of readings response dict
    """
    return await ReadingsTable.retrieve_by_meter_id(conn, meter_id)


@router.get("/meter/{meter_id}", response_model=MeterWithReadingsResp)
async def get_meter_with_readings(
    meter_id: uuid.UUID, conn: Connection = Depends(db_connect)
) -> dict[str, Any]:
    """List a given meter and all corresponding readings.

    Args:
        meter_id: uuid of meter
        conn: database connection

    Returns:
        dict with meter resonse dict and list of its' corresponding
        reading response dicts all together
    """
    return {
        "meter": await MetersTable.retrieve_by_id(conn, meter_id),
        "readings": await ReadingsTable.retrieve_by_meter_id(conn, meter_id),
    }
