import logging
import uuid
from typing import Annotated, Any, AsyncGenerator

from fastapi import APIRouter, Depends
from psycopg import AsyncConnection, Connection

from ..config import settings
from ..db import connect_to_db, get_conn_info
from ..db_models.users import UsersTable
from ..models.users import UserCreateRequestBody, UserResponseJson
from ..utils import log_async_func
from .auth import get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter()


@log_async_func(logger.info)
async def get_all_users() -> AsyncGenerator[list[UserResponseJson], None]:
    """List all users in the database.

    Returns: list of user dicts
    """
    async with await AsyncConnection.connect(conninfo=get_conn_info(settings)) as conn:
        yield await UsersTable.select_all(conn)


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
