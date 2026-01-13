import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from ..db import connect_to_db
from ..db_models.users import UsersTable
from ..models.users import (
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
    user: UserCreateRequestBody, conn: Annotated[Connection, Depends(connect_to_db)]
) -> UserResponseJson:
    """Add new user into the database.

    Args:
        user: user create request payload from client
        conn: database connection

    Returns: user dict
    """
    # TODO: fixme
    password = user.password
    user.password = get_password_hash(password)
    return await UsersTable.insert(conn, user)


@router.delete("/user/{id}")
@log_async_func(logger.info)
async def delete_user(
    id: uuid.UUID, conn: Annotated[Connection, Depends(connect_to_db)]
) -> dict[str, Any]:
    """Delete a user from the database.

    Args:
        id: uuid of user
        conn: database connection

    Returns:
        dict with detail
    """
    await UsersTable.delete(conn, id)
    return {"message": f"User {id} deleted successfully"}


@router.put("/user/{id}", response_model=UserResponseJson)
@log_async_func(logger.info)
async def update_user(
    id: uuid.UUID,
    user: UserUpdateRequestBody,
    conn: Annotated[Connection, Depends(connect_to_db)],
) -> UserResponseJson:
    """Update a meter in the database.

    Args:
        id: uuid of meter
        user: user update request payload from client
        conn: database connection

    Returns: meter dict
    """
    return await UsersTable.update(conn, id, user)
