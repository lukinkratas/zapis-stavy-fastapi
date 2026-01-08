import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from ..db import connect_to_db
from ..db_models.readings import ReadingsTable
from ..models.readings import (
    ReadingCreateRequestBody,
    ReadingResponseJson,
    ReadingUpdateRequestBody,
)
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/reading", status_code=201, response_model=ReadingResponseJson)
@log_async_func(logger.info)
async def create_reading(
    reading: ReadingCreateRequestBody,
    conn: Annotated[Connection, Depends(connect_to_db)],
) -> ReadingResponseJson:
    """Add new reading into the database.

    Args:
        reading: reading create request payload from client
        conn: database connection

    Returns: reading response dict
    """
    return await ReadingsTable.insert(conn, reading)


@router.delete("/reading/{id}")
@log_async_func(logger.info)
async def delete_reading(
    id: uuid.UUID, conn: Annotated[Connection, Depends(connect_to_db)]
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
@log_async_func(logger.info)
async def update_reading(
    id: uuid.UUID,
    reading: ReadingUpdateRequestBody,
    conn: Annotated[Connection, Depends(connect_to_db)],
) -> ReadingResponseJson:
    """Update a reading in the database.

    Args:
        id: uuid of reading
        reading: reading update request payload from client
        conn: database connection

    Returns: reading response dict
    """
    return await ReadingsTable.update(conn, id, reading)
