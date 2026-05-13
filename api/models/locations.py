import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import build_set_clause, format_sql_query, log_async_func

logger = logging.getLogger(__name__)


class LocationsTable:
    """General database model."""

    def __init__(self) -> None:
        self.table_name = "locations"

    @log_async_func(logger.debug)
    async def insert(
        self, db_conn: AsyncConnection, user_id: uuid.UUID, name: str
    ) -> dict[str, Any] | None:
        """Insert new record into db."""
        query = sql.SQL("""
            INSERT INTO {table} (user_id, name)
            VALUES (%(user_id)s, %(name)s)
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, dict(user_id=user_id, name=name))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def delete(
        self, db_conn: AsyncConnection, location_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Delete record from db."""
        query = sql.SQL("""
            DELETE FROM {table}
            WHERE id = %(location_id)s AND user_id = %(user_id)s
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, {"location_id": location_id, "user_id": user_id})
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def update(
        self,
        db_conn: AsyncConnection,
        location_id: uuid.UUID,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update record in db."""
        query = sql.SQL("""
            UPDATE {table}
            SET {set_clause}
            WHERE id = %(location_id)s AND user_id = %(user_id)s
            RETURNING *;
        """).format(
            table=sql.Identifier(self.table_name),
            set_clause=build_set_clause(data.keys()),
        )
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                query, data | {"location_id": location_id, "user_id": user_id}
            )
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_id(
        self,
        db_conn: AsyncConnection,
        location_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """Select user record by id from db."""
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE id = %(location_id)s
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, {"location_id": location_id})
            return await cur.fetchone()


locations_table = LocationsTable()
