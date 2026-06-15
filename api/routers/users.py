"""Routers layer for handling users lifecycle - register, update and delete.

Pydantic validation is handled in this module.
Database connection is passed to downstream user service.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..auth import get_current_user
from ..db import connect_to_db
from ..exceptions import user_not_found_exception
from ..repositories.users import UserRow
from ..schemas import BaseResponse, UpdateCreds
from ..services.users import delete_user, update_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/user")


@router.put("")
async def update(
    creds: UpdateCreds,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[UserRow, Depends(get_current_user)],
) -> BaseResponse:
    """Update a user.

    Args:
        creds: credentials update payload from client
        db_conn: database connection
        current_user: current authorized user

    Returns: response with detail

    Raises:
        HTTPException: if user was not found or email already exists.
    """
    try:
        user = await update_user(db_conn, current_user.id, creds)

        if not user:
            raise user_not_found_exception

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="User email already in use")

    return BaseResponse(detail="User updated")


@router.delete("")
async def delete(
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[UserRow, Depends(get_current_user)],
) -> BaseResponse:
    """Delete a user.

    Args:
        db_conn: database connection
        current_user: current authorized user

    Returns: response with detail

    Raises:
        HTTPException: if user was not found
    """
    user = await delete_user(db_conn, current_user.id)

    if not user:
        raise user_not_found_exception

    return BaseResponse(detail="User deleted")
