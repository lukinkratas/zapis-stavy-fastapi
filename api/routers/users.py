import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..db import connect_to_db
from ..models.users import users_table
from ..schemas.users import (
    UserCreateRequestBody,
    UserResponseJson,
    UserUpdateRequestBody,
)
from ..utils import log_async_func
from .auth import get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201, response_model=UserResponseJson)
@log_async_func(logger.info)
async def register_user(
    user: UserCreateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> dict[str, Any]:
    """Add new user into the database.

    Args:
        user: user create request payload from client
        conn: database connection

    Returns: user dict

    Raises:
        HTTPException: if user cannot be inserted in the database
    """
    # TODO: fixme
    password = user.password
    user.password = get_password_hash(password)
    data = user.model_dump()

    try:
        registered_user = await users_table.insert(conn, data)

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="User already exists")

    return registered_user


@router.delete("/user/{id}", status_code=204)
@log_async_func(logger.info)
async def delete_user(
    id: uuid.UUID, conn: Annotated[AsyncConnection, Depends(connect_to_db)]
) -> None:
    """Delete a user from the database.

    Args:
        id: uuid of user
        conn: database connection

    Returns: None

    Raises:
        HTTPException: if user cannot be deleted from the database
    """
    await users_table.delete(conn, id)


@router.put("/user/{id}", response_model=UserResponseJson)
@log_async_func(logger.info)
async def update_user(
    id: uuid.UUID,
    user: UserUpdateRequestBody,
    conn: Annotated[AsyncConnection, Depends(connect_to_db)],
) -> dict[str, Any]:
    """Update a meter in the database.

    Args:
        id: uuid of meter
        user: user update request payload from client
        conn: database connection

    Returns: meter dict

    Raises:
        HTTPException: if user cannot be updated in the database
    """
    data = user.model_dump()
    updated_user = await users_table.update(conn, id, data)

    if updated_user is None:
        raise HTTPException(status_code=404, detail="Cannot update user")

    return updated_user
