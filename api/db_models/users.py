import logging
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..models.users import UserCreateRequestBody
from ..utils import format_sql_query, log_async_func
from .const import INSERT_QUERY

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
