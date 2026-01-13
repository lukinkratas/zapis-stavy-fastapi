import logging
import uuid
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..models.users import UserCreateRequestBody, UserUpdateRequestBody
from ..utils import build_set_clause, format_sql_query, log_async_func
from .const import DELETE_QUERY, INSERT_QUERY, UPDATE_QUERY

logger = logging.getLogger(__name__)


class UsersTable:
    """Users database model."""

    @classmethod
    @log_async_func(logger.debug)
    async def insert(
        cls, conn: AsyncConnection, user: UserCreateRequestBody
    ) -> dict[str, Any]:
        """Insert new meter record into db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = user.model_dump()
            query = INSERT_QUERY.format(
                table=sql.Identifier("users"),
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                value_placeholders=sql.SQL(", ").join(
                    map(sql.Placeholder, data.keys())
                ),
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data)

            new_user = await cur.fetchone()
            if new_user is None:
                raise HTTPException(status_code=404, detail="User cannot be created")

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return new_user

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete meter record from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = DELETE_QUERY.format(table=sql.Identifier("users"))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"id": id})
            await conn.commit()

    @classmethod
    @log_async_func(logger.debug)
    async def update(
        cls, conn: AsyncConnection, id: uuid.UUID, user: UserUpdateRequestBody
    ) -> dict[str, Any]:
        """Update user record in db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = user.model_dump()

            query = UPDATE_QUERY.format(
                table=sql.Identifier("users"), set_clause=build_set_clause(data.keys())
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data | {"id": id})

            updated_reading = await cur.fetchone()
            if updated_reading is None:
                raise HTTPException(
                    status_code=404, detail=f"User {id} cannot be updated"
                )

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return updated_reading

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
