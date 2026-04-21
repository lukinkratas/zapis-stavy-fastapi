import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..db import connect_to_db
from ..models.locations import locations_table
from ..schemas.locations import (
    LocationCreateRequestBody,
    LocationResponseJson,
    LocationUpdateRequestBody,
)
from ..utils import log_async_func
from .auth import get_current_confirmed_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/location")


@router.post("", status_code=201, response_model=LocationResponseJson)
@log_async_func(logger.info)
async def create_location(
    location: LocationCreateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> dict[str, Any] | None:
    """Add new location into the database.

    Args:
        location: location create request payload from client
        conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: location dict

    Raises:
        HTTPException: if location cannot be inserted in the database
    """
    data = location.model_dump()
    data["user_id"] = current_confirmed_user["id"]

    try:
        created_location = await locations_table.insert(conn, data)

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Location already exists")

    return created_location


@router.delete("/{id}", status_code=200)
@log_async_func(logger.info)
async def delete_location(
    id: uuid.UUID,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> None:
    """Delete a location from the database.

    Args:
        id: uuid of location
        conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: None

    Raises:
        HTTPException: if location cannot be deleted from the database
    """
    await locations_table.delete(conn, id, current_confirmed_user["id"])


@router.put("/{id}", response_model=LocationResponseJson)
@log_async_func(logger.info)
async def update_location(
    id: uuid.UUID,
    location: LocationUpdateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> dict[str, Any]:
    """Update a location in the database.

    Args:
        id: uuid of location
        location: location update request payload from client
        conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: location dict

    Raises:
        HTTPException: if location cannot be updated in the database
    """
    data = location.model_dump()
    updated_location = await locations_table.update(conn, id, current_confirmed_user["id"], data)

    if updated_location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    return updated_location
