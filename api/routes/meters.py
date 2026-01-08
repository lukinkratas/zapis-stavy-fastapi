import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from ..db import connect_to_db
from ..db_models.meters import MetersTable
from ..db_models.readings import ReadingsTable
from ..models.meters import (
    MeterCreateRequestBody,
    MeterResponseJson,
    MeterUpdateRequestBody,
    MeterWithReadingsResponseJson,
)
from ..models.readings import (
    ReadingResponseJson,
)
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/meter", status_code=201, response_model=MeterResponseJson)
@log_async_func(logger.info)
async def create_meter(
    meter: MeterCreateRequestBody, conn: Annotated[Connection, Depends(connect_to_db)]
) -> MeterResponseJson:
    """Add new meter into the database.

    Args:
        meter: meter create request payload from client
        conn: database connection

    Returns: meter response dict
    """
    return await MetersTable.insert(conn, meter)


@router.delete("/meter/{id}")
@log_async_func(logger.info)
async def delete_meter(
    id: uuid.UUID, conn: Annotated[Connection, Depends(connect_to_db)]
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
@log_async_func(logger.info)
async def update_meter(
    id: uuid.UUID,
    meter: MeterUpdateRequestBody,
    conn: Annotated[Connection, Depends(connect_to_db)],
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
@log_async_func(logger.info)
async def get_all_meters(
    conn: Annotated[Connection, Depends(connect_to_db)],
) -> list[MeterResponseJson]:
    """List all meter dicts in the database.

    Args:
        conn: database connection

    Returns: list of meter response dicts
    """
    return await MetersTable.select_all(conn)


@router.get("/meter/{id}/reading", response_model=list[ReadingResponseJson])
@log_async_func(logger.info)
async def get_readings_on_meter(
    id: uuid.UUID, conn: Annotated[Connection, Depends(connect_to_db)]
) -> list[ReadingResponseJson]:
    """List all readings on a given meter.

    Args:
        id: uuid of meter
        conn: database connection

    Returns: list of readings response dict
    """
    return await ReadingsTable.select_by_meter_id(conn, id)


@router.get("/meter/{id}", response_model=MeterWithReadingsResponseJson)
@log_async_func(logger.info)
async def get_meter_with_readings(
    id: uuid.UUID, conn: Annotated[Connection, Depends(connect_to_db)]
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
