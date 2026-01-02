import uuid
from typing import Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from .db import db_connect
from .db_models import MetersTable, ReadingsTable
from .models import (
    MeterCreateRequestBody,
    MeterResponseJson,
    MeterUpdateRequestBody,
    MeterWithReadingsResponseJson,
    ReadingCreateRequestBody,
    ReadingUpdateRequestBody,
    ReadingResponseJson,
)

router = APIRouter()


@router.post("/meter", status_code=201, response_model=MeterResponseJson)
async def create_meter(
    meter: MeterCreateRequestBody, conn: Connection = Depends(db_connect)
) -> MeterResponseJson:
    """Add new meter into the database.

    Args:
        meter: meter create request payload from client
        conn: database connection

    Returns: meter response dict
    """
    return await MetersTable.insert(conn, meter)


@router.delete("/meter/{id}")
async def delete_meter(
    id: uuid.UUID, conn: Connection = Depends(db_connect)
) -> dict[str, Any]:
    """Delete a meter from the database.

    Args:
        id: uuid of meter
        conn: database connection

    Returns:
        dict with detail
    """
    await MetersTable.delete(conn, id)
    return {"message": f"Meter {id} deleted successfully"}


@router.put("/meter/{id}", response_model=MeterResponseJson)
async def update_meter(
    id: uuid.UUID, meter: MeterUpdateRequestBody, conn: Connection = Depends(db_connect)
) -> MeterResponseJson:
    """Update a meter in the database.

    Args:
        id: uuid of meter
        meter: meter update request payload from client
        conn: database connection

    Returns: meter response dict
    """
    return await MetersTable.update(conn, id, meter)


@router.get("/meter", response_model=list[MeterResponseJson])
async def get_all_meters(
    conn: Connection = Depends(db_connect),
) -> list[MeterResponseJson]:
    """List all meter dicts in the database.

    Args:
        conn: database connection

    Returns: list of meter response dicts
    """
    return await MetersTable.select_all(conn)


@router.post("/reading", status_code=201, response_model=ReadingResponseJson)
async def create_reading(
    reading: ReadingCreateRequestBody, conn: Connection = Depends(db_connect)
) -> ReadingResponseJson:
    """Add new reading into the database.

    Args:
        reading: reading create request payload from client
        conn: database connection

    Returns: reading response dict
    """
    return await ReadingsTable.insert(conn, reading)


@router.delete("/reading/{id}")
async def delete_reading(
    id: uuid.UUID, conn: Connection = Depends(db_connect)
) -> dict[str, Any]:
    """Delete a reading from the database.

    Args:
        id: uuid of reading
        conn: database connection

    Returns:
        dict with detail
    """
    await ReadingsTable.delete(conn, id)
    return {"message": f"Reading {id} deleted successfully"}

@router.put("/reading/{id}", response_model=ReadingResponseJson)
async def update_reading(
    id: uuid.UUID, reading: ReadingUpdateRequestBody, conn: Connection = Depends(db_connect)
) -> ReadingResponseJson:
    """Update a reading in the database.

    Args:
        id: uuid of reading
        reading: reading update request payload from client
        conn: database connection

    Returns: reading response dict
    """
    return await ReadingsTable.update(conn, id, reading)

@router.get("/meter/{id}/reading", response_model=list[ReadingResponseJson])
async def get_readings_on_meter(
    id: uuid.UUID, conn: Connection = Depends(db_connect)
) -> list[ReadingResponseJson]:
    """List all readings on a given meter.

    Args:
        id: uuid of meter
        conn: database connection

    Returns: list of readings response dict
    """
    return await ReadingsTable.select_by_meter_id(conn, id)


@router.get("/meter/{id}", response_model=MeterWithReadingsResponseJson)
async def get_meter_with_readings(
    id: uuid.UUID, conn: Connection = Depends(db_connect)
) -> dict[str, Any]:
    """List a given meter and all corresponding readings.

    Args:
        id: uuid of meter
        conn: database connection

    Returns:
        dict with meter resonse dict and list of its' corresponding
        reading response dicts all together
    """
    return {
        "meter": await MetersTable.select_by_id(conn, id),
        "readings": await ReadingsTable.select_by_meter_id(conn, id),
    }
