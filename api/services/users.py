"""
Service layer for handling users lifecycle - register, update and delete.
Database transaction is handled in this module.
"""
import logging
import uuid
from typing import Any

from psycopg import AsyncConnection

from ..models.users import users_table
from ..security import get_password_hash
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_user_by_id(
    db_conn: AsyncConnection, user_id: uuid.UUID
) -> dict[str, Any] | None:
    """Select user from the database by id.
    
    Args:
        db_conn: database connection
        user_id: user id to be updated

    Returns: user dict
    """
    return await users_table.select_by_id(db_conn, user_id)


@log_async_func(logger.debug)
async def select_user_by_email(
    db_conn: AsyncConnection, email: str
) -> dict[str, Any] | None:
    """Select user from the database by email.
    
    Args:
        db_conn: database connection
        email: email of the user being selected

    Returns: user dict
    """
    return await users_table.select_by_email(db_conn, email)


@log_async_func(logger.debug)
async def register_user(
    db_conn: AsyncConnection, email: str, password: str
) -> dict[str, Any]:
    """Add new user into the database.

    Args:
        db_conn: database connection
        email: email of the user being registered
        password: plain password of the user being registered

    Returns: user dict
    """
    async with db_conn.transaction():
        return await users_table.insert(db_conn, email, get_password_hash(password))


@log_async_func(logger.debug)
async def update_user(
    db_conn: AsyncConnection, user_id: uuid.UUID, data: dict[str, Any]
) -> dict[str, Any]:
    """Update a user in the database.

    Args:
        db_conn: database connection
        user_id: user id to be updated
        data: field-value pairs to be updated

    Returns: user dict
    """
    data_copy = data.copy()

    if "password" in data.keys():
        password = data_copy.pop("password")
        data_copy["password_hash"] = get_password_hash(password)

    async with db_conn.transaction():
        return await users_table.update(db_conn, user_id, data_copy)


@log_async_func(logger.debug)
async def delete_user(db_conn: AsyncConnection, user_id: uuid.UUID) -> dict[str, Any]:
    """Delete a user from the database.

    Args:
        db_conn: database connection
        user_id: user id to be updated

    Returns: user dict
    """
    async with db_conn.transaction():
        return await users_table.delete(db_conn, user_id)


@log_async_func(logger.debug)
async def confirm_user(
    db_conn: AsyncConnection, user_id: uuid.UUID
) -> dict[str, Any] | None:    
    """Confirm a user in the database.

    Args:
        db_conn: database connection
        user_id: user id to be confirmed

    Returns: user dict
    """
    async with db_conn.transaction():
        return await users_table.update(db_conn, user_id, {"confirmed": True})
