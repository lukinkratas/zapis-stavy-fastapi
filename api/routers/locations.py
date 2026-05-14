"""
Routers layer for handling location lifecycle - register, update and delete.
Pydantic validation is handled in this module.
Database connection is passed to downstream user service.
"""
import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..auth import get_current_confirmed_user
from ..db import connect_to_db
from ..exceptions import location_exists_exception, location_not_found_exception
from ..schemas import (
    BaseResponse,
    LocationCreateRequest,
    LocationUpdateRequest,
    ResponseWithId,
)
from ..services.locations import create_location, delete_location, update_location

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/location")


@router.post("", status_code=201, response_model=ResponseWithId)
async def create(
    location: LocationCreateRequest,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> dict[str, Any] | None:
    """Create new location.

    Args:
        location: location create request payload from client
        db_conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: response with detail and location_id

    Raises:
        HTTPException: if location already exists
    """
    try:
        location = await create_location(
            db_conn, current_confirmed_user["id"], **location.model_dump()
        )

    except UniqueViolation:
        raise location_exists_exception

    return {
        "detail": "Location created.",
        "id": location["id"],
    }


@router.put("/{id}", response_model=BaseResponse)
async def update(
    id: uuid.UUID,
    location: LocationUpdateRequest,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> dict[str, Any]:
    """Update a location.

    Args:
        id: uuid of location
        location: location update request payload from client
        db_conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: response with detail

    Raises:
        HTTPException: if location was not found or name already exists.
    """
    try:
        location = await update_location(
            db_conn,
            id,
            current_confirmed_user["id"],
            location.model_dump(exclude_unset=True),
        )

        if not location:
            raise location_not_found_exception

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Name already in use")

    return {"detail": "Location updated"}


@router.delete("/{id}", response_model=BaseResponse)
async def delete(
    id: uuid.UUID,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_confirmed_user: Annotated[
        dict[str, Any], Depends(get_current_confirmed_user)
    ],
) -> None:
    """Delete a location.

    Args:
        id: uuid of location
        db_conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: response with detail

    Raises:
        HTTPException: if location was not found
    """
    location = await delete_location(db_conn, id, current_confirmed_user["id"])

    if not location:
        raise location_not_found_exception

    return {"detail": "Location deleted"}
