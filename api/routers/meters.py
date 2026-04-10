import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..auth import get_current_user
from ..db import connect_to_db
from ..models.meters import meters_table
from ..schemas.meters import (
    MeterCreateRequestBody,
    MeterResponseJson,
    MeterUpdateRequestBody,
)
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/meter")


@router.post("", status_code=201, response_model=MeterResponseJson)
@log_async_func(logger.info)
async def create_meter(
    meter: MeterCreateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any] | None:
    """Add new meter into the database.

    Args:
        meter: meter create request payload from client
        conn: database connection
        current_user: current authorized user

    Returns: meter dict

    Raises:
        HTTPException: if meter cannot be inserted in the database
    """
    data = meter.model_dump()
    data["user_id"] = current_user["id"]

    try:
        created_meter = await meters_table.insert(conn, data)

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Meter already exists")

    return created_meter


@router.delete("/{id}", status_code=204)
@log_async_func(logger.info)
async def delete_meter(
    id: uuid.UUID,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> None:
    """Delete a meter from the database.

    Args:
        id: uuid of meter
        conn: database connection
        current_user: current authorized user

    Returns: None

    Raises:
        HTTPException: if meter cannot be deleted from the database
    """
    await meters_table.delete(conn, id, current_user["id"])


@router.put("/{id}", response_model=MeterResponseJson)
@log_async_func(logger.info)
async def update_meter(
    id: uuid.UUID,
    meter: MeterUpdateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Update a meter in the database.

    Args:
        id: uuid of meter
        meter: meter update request payload from client
        conn: database connection
        current_user: current authorized user

    Returns: meter dict

    Raises:
        HTTPException: if meter cannot be updated in the database
    """
    data = meter.model_dump()
    updated_meter = await meters_table.update(conn, id, current_user["id"], data)

    if updated_meter is None:
        raise HTTPException(status_code=404, detail="Cannot update meter")

    return updated_meter
