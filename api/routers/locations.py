import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..db import connect_to_db
from ..schemas.locations import (
    LocationCreateRequest,
    LocationResponse,
    LocationUpdateRequest,
)
from ..utils import log_async_func
from .auth import get_current_confirmed_user
from ..services.locations import create_location, update_location, delete_location
from ..schemas.base import BaseResponse, ResponseWithId

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/location")


@router.post("", status_code=201, response_model=ResponseWithId)
@log_async_func(logger.info)
async def create_location(
    location: LocationCreateRequest,
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
    try:
        created_location = await create_location(conn, current_confirmed_user["id"], data=location.model_dump())

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Location already exists")

    return {
        "detail": "Location created.",
        "id": str(created_location["id"]),
    }


@router.delete("/{id}", reponse_model=BaseResponse)
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
    await delete_location(conn, id, current_confirmed_user["id"])
    return {"detail": "Location deleted"}


@router.put("/{id}", response_model=BaseResponse)
@log_async_func(logger.info)
async def update_location(
    id: uuid.UUID,
    location: LocationUpdateRequest,
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
    await update_location(conn, id, current_confirmed_user["id"], data=location.model_dump(exclude_unset=True))
    return {"detail": "Location updated"}
