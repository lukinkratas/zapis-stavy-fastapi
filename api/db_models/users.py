import logging
import uuid
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..models.users import UserCreateRequestBody, UserUpdateRequestBody
from ..utils import format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class UsersTable:
    """Users database model."""

    @classmethod
    @log_async_func(logger.debug)
    async def insert(
        cls, conn: AsyncConnection, user: UserCreateRequestBody
    ) -> dict[str, Any]:
        """Insert new meter record into db."""
        return await BaseTable.insert(conn, data=user.model_dump(), table="users")

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete meter record from db."""
        return await BaseTable.delete(conn, id, table="users")

    @classmethod
    @log_async_func(logger.debug)
    async def update(
        cls, conn: AsyncConnection, id: uuid.UUID, user: UserUpdateRequestBody
    ) -> dict[str, Any]:
        """Update user record in db."""
        return await BaseTable.update(conn, id, data=user.model_dump(), table="users")

    @classmethod
    @log_async_func(logger.debug)
    async def select_by_email(cls, conn: AsyncConnection, email: str) -> dict[str, Any]:
        """Select user record by email from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM users
                WHERE email = %(email)s;
            """)
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"email": email})

            user = await cur.fetchone()
            if user is None:
                raise HTTPException(status_code=404, detail=f"User {id} not found")
            return user
