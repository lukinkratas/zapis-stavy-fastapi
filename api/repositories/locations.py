"""Database tables layer for handling location lifecycle - insert, update and delete."""

import logging
import uuid
from datetime import datetime
from typing import Any, NamedTuple

from psycopg import AsyncConnection, sql
from psycopg.rows import class_row

from ..utils import build_set_clause, format_sql_query, log_async_func

logger = logging.getLogger(__name__)


class LocationRow(NamedTuple):
    """Location row database model."""

    id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID
    location_name: str


class LocationsTable:
    """Location database table."""

    def __init__(self) -> None:
        self.table_name = "locations"

    @log_async_func(logger.debug)
    async def insert(
        self, db_conn: AsyncConnection, user_id: uuid.UUID, location_name: str
    ) -> LocationRow | None:
        """Insert new location record into db.

        Args:
            db_conn: database connection
            user_id: location owner's user id
            location_name: name of the location being inserted

        Returns: location row
        """
        query = sql.SQL("""
            INSERT INTO {table} (user_id, location_name)
            VALUES (%(user_id)s, %(location_name)s)
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(LocationRow)) as cur:
            await cur.execute(query, dict(user_id=user_id, location_name=location_name))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def update(
        self,
        db_conn: AsyncConnection,
        location_id: uuid.UUID,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> LocationRow | None:
        """Update location record in db.

        Args:
            db_conn: database connection
            location_id: location id to be updated
            user_id: user id to be updated
            data: field-value pairs to be updated

        Returns: location row
        """
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

        async with db_conn.cursor(row_factory=class_row(LocationRow)) as cur:
            await cur.execute(
                query, data | dict(location_id=location_id, user_id=user_id)
            )
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def delete(
        self, db_conn: AsyncConnection, location_id: uuid.UUID, user_id: uuid.UUID
    ) -> LocationRow | None:
        """Delete location record from db.

        Args:
            db_conn: database connection
            location_id: location id to be deleted
            user_id: location owner's user id

        Returns: location row
        """
        query = sql.SQL("""
            DELETE FROM {table}
            WHERE id = %(location_id)s AND user_id = %(user_id)s
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(LocationRow)) as cur:
            await cur.execute(query, dict(location_id=location_id, user_id=user_id))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_id(
        self,
        db_conn: AsyncConnection,
        location_id: uuid.UUID,
    ) -> LocationRow | None:
        """Select location record by id from db.

        Args:
            db_conn: database connection
            location_id: location id to be selected

        Returns: location row
        """
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE id = %(location_id)s
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(LocationRow)) as cur:
            await cur.execute(query, dict(location_id=location_id))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select(
        self,
        db_conn: AsyncConnection,
        user_id: uuid.UUID,
    ) -> list[LocationRow] | None:
        """Select location records from db.

        Args:
            db_conn: database connection
            user_id: user id to be updated

        Returns: location row
        """
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE user_id = %(user_id)s
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(LocationRow)) as cur:
            await cur.execute(query, dict(user_id=user_id))
            return await cur.fetchall()


locations_table = LocationsTable()
