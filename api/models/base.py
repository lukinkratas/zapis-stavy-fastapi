import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import build_set_clause, format_sql_query, log_async_func

logger = logging.getLogger(__name__)


class BaseTable:
    """General database model."""

    def __init__(self, table: str):
        self.table = table

    async def insert(
        self, conn: AsyncConnection, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Insert new record into db."""
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    INSERT INTO {table} ({columns})
                    VALUES ({value_placeholders})
                    RETURNING *;
                """).format(
                    table=sql.Identifier(self.table),
                    columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                    value_placeholders=sql.SQL(", ").join(
                        map(sql.Placeholder, data.keys())
                    ),
                )
                logger.debug(f"SQL query: {format_sql_query(query)}")
                await cur.execute(query, data)
                return await cur.fetchone()

    @log_async_func(logger.debug)
    async def delete(
        self, conn: AsyncConnection, id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Delete record from db."""
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    DELETE FROM {table}
                    WHERE id = %(id)s AND user_id = %(user_id)s;
                """).format(table=sql.Identifier(self.table))
                logger.debug(f"SQL query: {format_sql_query(query)}")
                await cur.execute(query, {"id": id, "user_id": user_id})

    @log_async_func(logger.debug)
    async def update(
        self,
        conn: AsyncConnection,
        id: uuid.UUID,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update record in db."""
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    UPDATE {table}
                    SET {set_clause}
                    WHERE id = %(id)s AND user_id = %(user_id)s
                    RETURNING *;
                """).format(
                    table=sql.Identifier(self.table),
                    set_clause=build_set_clause(data.keys()),
                )
                logger.debug(f"SQL query: {format_sql_query(query)}")
                await cur.execute(query, data | {"id": id, "user_id": user_id})
                return await cur.fetchone()
