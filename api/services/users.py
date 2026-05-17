"""Service layer for handling users lifecycle - register, update and delete.

Database transaction is handled in this module.
"""

import logging
import uuid

from psycopg import AsyncConnection

from ..repositories.users import UserRow, users_table
from ..schemas import RegisterCreds, UpdateCreds
from ..security import get_password_hash
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_user_by_id(
    db_conn: AsyncConnection, user_id: uuid.UUID
) -> UserRow | None:
    """Select user from the database by id.

    Args:
        db_conn: database connection
        user_id: user id to be updated

    Returns: user row
    """
    return await users_table.select_by_id(db_conn, user_id)


@log_async_func(logger.debug)
async def select_user_by_email(db_conn: AsyncConnection, email: str) -> UserRow | None:
    """Select user from the database by email.

    Args:
        db_conn: database connection
        email: email of the user being selected

    Returns: user row
    """
    return await users_table.select_by_email(db_conn, email)


@log_async_func(logger.debug)
async def register_user(
    db_conn: AsyncConnection, creds: RegisterCreds
) -> UserRow | None:
    """Add new user into the database.

    Args:
        db_conn: database connection
        creds: register credentials payload from router

    Returns: user row
    """
    data = creds.model_dump(exclude_unset=True)
    password = data.pop("password")
    data["password_hash"] = get_password_hash(password)

    async with db_conn.transaction():
        return await users_table.insert(db_conn, **data)


@log_async_func(logger.debug)
async def update_user(
    db_conn: AsyncConnection, user_id: uuid.UUID, creds: UpdateCreds
) -> UserRow | None:
    """Update a user in the database.

    Args:
        db_conn: database connection
        user_id: user id to be updated
        creds: credentials update payload from router

    Returns: user row
    """
    data = creds.model_dump(exclude_unset=True)

    if "password" in data.keys():
        password = data.pop("password")
        data["password_hash"] = get_password_hash(password)

    async with db_conn.transaction():
        return await users_table.update(db_conn, user_id, data)


@log_async_func(logger.debug)
async def delete_user(db_conn: AsyncConnection, user_id: uuid.UUID) -> UserRow | None:
    """Delete a user from the database.

    Args:
        db_conn: database connection
        user_id: user id to be updated

    Returns: user row
    """
    async with db_conn.transaction():
        return await users_table.delete(db_conn, user_id)
