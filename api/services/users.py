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
    return await users_table.select_by_id(db_conn, user_id)


@log_async_func(logger.debug)
async def select_user_by_email(
    db_conn: AsyncConnection, email: str
) -> dict[str, Any] | None:
    return await users_table.select_by_email(db_conn, email)


@log_async_func(logger.debug)
async def register_user(
    db_conn: AsyncConnection, email: str, password: str
) -> dict[str, Any]:
    async with db_conn.transaction():
        return await users_table.insert(db_conn, email, get_password_hash(password))


@log_async_func(logger.debug)
async def update_user(
    db_conn: AsyncConnection, user_id: uuid.UUID, data: dict[str, Any]
) -> dict[str, Any]:
    data_copy = data.copy()

    if "password" in data.keys():
        password = data_copy.pop("password")
        data_copy["password_hash"] = get_password_hash(password)

    async with db_conn.transaction():
        return await users_table.update(db_conn, user_id, data_copy)


@log_async_func(logger.debug)
async def delete_user(db_conn: AsyncConnection, user_id: uuid.UUID) -> dict[str, Any]:
    async with db_conn.transaction():
        return await users_table.delete(db_conn, user_id)


@log_async_func(logger.debug)
async def confirm_user(
    db_conn: AsyncConnection, user_id: uuid.UUID
) -> dict[str, Any] | None:
    async with db_conn.transaction():
        return await users_table.update(db_conn, user_id, {"confirmed": True})
