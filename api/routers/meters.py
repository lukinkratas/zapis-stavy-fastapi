import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection

from ..db import connect_to_db
from ..db_models.meters import meters_table
from ..db_models.readings import readings_table
from ..models.meters import (
    MeterCreateRequestBody,
    MeterResponseJson,
    MeterUpdateRequestBody,
    MeterWithReadingsResponseJson,
)
from ..models.readings import ReadingResponseJson
from ..utils import log_async_func
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/meter", status_code=201, response_model=MeterResponseJson)
@log_async_func(logger.info)
async def create_meter(
    meter: MeterCreateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Add new meter into the database.

    Args:
        meter: meter create request payload from client
        conn: database connection
        current_user: current authorized user

    Returns: meter dict
    """
    data = meter.model_dump()
    data["user_id"] = current_user["id"]
    return await meters_table.insert(conn, data)


@router.delete("/meter/{id}")
@log_async_func(logger.info)
async def delete_meter(
    id: uuid.UUID, conn: Annotated[AsyncConnection, Depends(connect_to_db)]
) -> dict[str, Any]:
    """Delete a meter from the database.

    Args:
        id: uuid of meter
        conn: database connection

    Returns:
        dict with detail
    """
    await meters_table.delete(conn, id)
    return {"message": f"Meter {id} deleted successfully"}


@router.put("/meter/{id}", response_model=MeterResponseJson)
@log_async_func(logger.info)
async def update_meter(
    id: uuid.UUID,
    meter: MeterUpdateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> dict[str, Any]:
    """Update a meter in the database.

    Args:
        id: uuid of meter
        meter: meter update request payload from client
        conn: database connection

    Returns: meter dict
    """
    return await meters_table.update(conn, id, data=meter.model_dump())


@router.get("/meter/{id}/reading", response_model=list[ReadingResponseJson])
@log_async_func(logger.info)
async def get_readings_on_meter(
    id: uuid.UUID, conn: Annotated[AsyncConnection, Depends(connect_to_db)]
) -> list[dict[str, Any]]:
    """List all readings on a given meter.

    Args:
        id: uuid of meter
        conn: database connection

    Returns: list of reading dicts
    """
    return await readings_table.select_by_meter_id(conn, id)


@router.get("/meter/{id}", response_model=MeterWithReadingsResponseJson)
@log_async_func(logger.info)
async def get_meter_with_readings(
    id: uuid.UUID, conn: Annotated[AsyncConnection, Depends(connect_to_db)]
) -> dict[str, Any]:
    """List a given meter and all corresponding readings.

    Args:
        id: uuid of meter
        conn: database connection

    Returns:
        dict with meter dict and list of its' corresponding
        readings dicts all together
    """
    return {
        "meter": await meters_table.select_by_id(conn, id),
        "readings": await readings_table.select_by_meter_id(conn, id),
    }
