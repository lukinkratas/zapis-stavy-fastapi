import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection

from ..db import connect_to_db
from ..db_models.readings import readings_table
from ..models.readings import (
    ReadingCreateRequestBody,
    ReadingResponseJson,
    ReadingUpdateRequestBody,
)
from ..utils import log_async_func
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/reading", status_code=201, response_model=ReadingResponseJson)
@log_async_func(logger.info)
async def create_reading(
    reading: ReadingCreateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Add new reading into the database.

    Args:
        reading: reading create request payload from client
        conn: database connection
        current_user: current authorized user

    Returns: reading dict
    """
    data = reading.model_dump()
    data["user_id"] = current_user["id"]
    return await readings_table.insert(conn, data)


@router.delete("/reading/{id}")
@log_async_func(logger.info)
async def delete_reading(
    id: uuid.UUID, conn: Annotated[AsyncConnection, Depends(connect_to_db)]
) -> dict[str, Any]:
    """Delete a reading from the database.

    Args:
        id: uuid of reading
        conn: database connection

    Returns: dict with detail
    """
    await readings_table.delete(conn, id)
    return {"message": f"Reading {id} deleted successfully"}


@router.put("/reading/{id}", response_model=ReadingResponseJson)
@log_async_func(logger.info)
async def update_reading(
    id: uuid.UUID,
    reading: ReadingUpdateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> ReadingResponseJson:
    """Update a reading in the database.

    Args:
        id: uuid of reading
        reading: reading update request payload from client
        conn: database connection

    Returns: reading dict
    """
    return await readings_table.update(conn, id, data=reading.model_dump())
