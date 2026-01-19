import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import build_set_clause, format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class UsersTable(BaseTable):
    """Users database model."""

    def __init__(self) -> None:
        super().__init__(table="users")

    @log_async_func(logger.debug)
    async def delete(self, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete user record from db."""
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    DELETE FROM {table}
                    WHERE id = %(id)s;
                """).format(table=sql.Identifier(self.table))
                logger.debug(f"SQL query: {format_sql_query(query)}")
                await cur.execute(query, {"id": id})

    @log_async_func(logger.debug)
    async def update(
        self, conn: AsyncConnection, id: uuid.UUID, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update user record in db."""
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    UPDATE {table}
                    SET {set_clause}
                    WHERE id = %(id)s
                    RETURNING *;
                """).format(
                    table=sql.Identifier(self.table),
                    set_clause=build_set_clause(data.keys()),
                )
                logger.debug(f"SQL query: {format_sql_query(query)}")
                await cur.execute(query, data | {"id": id})
                return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_email(
        self, conn: AsyncConnection, email: str
    ) -> dict[str, Any]:
        """Select user record by email from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM {table}
                WHERE email = %(email)s;
            """).format(table=sql.Identifier(self.table))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"email": email})

            return await cur.fetchone()


users_table = UsersTable()
