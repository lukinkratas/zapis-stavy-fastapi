"""Routers layer for handling location lifecycle - create, update and delete.

Pydantic validation is handled in this module.
Database connection is passed to downstream user service.
"""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..auth import get_current_confirmed_user
from ..exceptions import location_exists_exception, location_not_found_exception
from ..schemas import BaseResponse, CreateProps, ResponseWithId, UpdateProps
from ..services.locations import create_location, delete_location, update_location
from ..db import get_db_session
from ..models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/location")


@router.post("", status_code=201)
async def create(
    props: CreateProps,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_confirmed_user: Annotated[User, Depends(get_current_confirmed_user)],
) -> ResponseWithId:
    """Create new location.

    Args:
        props: create location properties request payload from client
        db_conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: response with detail and location_id

    Raises:
        HTTPException: if location already exists
    """
    try:
        location = await create_location(db_session, current_confirmed_user.id, location)

    except IntegrityError:
        await db_session.rollback()
        raise location_exists_exception

    return ResponseWithId(detail="Location created", id=location.id)


@router.put("/{id}")
async def update(
    id: uuid.UUID,
    props: UpdateProps,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_confirmed_user: Annotated[User, Depends(get_current_confirmed_user)],
) -> BaseResponse:
    """Update a location.

    Args:
        id: uuid of location
        props: update location properties request payload from client
        db_conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: response with detail

    Raises:
        HTTPException: if location was not found or name already exists.
    """
    try:
        location = await update_location(db_session, id, current_confirmed_user.id, location)

        if not location:
            raise location_not_found_exception

    except IntegrityError:
        await db_session.rollback()
        raise location_exists_exception

    return BaseResponse(detail="Location updated")


@router.delete("/{id}")
async def delete(
    id: uuid.UUID,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_confirmed_user: Annotated[User, Depends(get_current_confirmed_user)],
) -> BaseResponse:
    """Delete a location.

    Args:
        id: uuid of location
        db_conn: database connection
        current_confirmed_user: current authorized and confirmed user

    Returns: response with detail

    Raises:
        HTTPException: if location was not found
    """
    deleted = await delete_location(db_session, id, current_confirmed_user.id)

    if not deleted:
        raise location_not_found_exception

    return BaseResponse(detail="Location deleted")
