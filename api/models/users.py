import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import build_set_clause, format_sql_query, log_async_func

logger = logging.getLogger(__name__)


class UsersTable:
    """Users database model."""

    def __init__(self) -> None:
        self.table_name = "users"

    @log_async_func(logger.debug)
    async def insert(
        self, db_conn: AsyncConnection, email: str, password_hash: str
    ) -> dict[str, Any] | None:
        """Insert new record into db."""
        query = sql.SQL("""
            INSERT INTO {table} (email, password_hash)
            VALUES (%(email)s, %(password_hash)s)
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, dict(email=email, password_hash=password_hash))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def delete(self, db_conn: AsyncConnection, user_id: uuid.UUID) -> None:
        """Delete user record from db."""
        query = sql.SQL("""
            DELETE FROM {table}
            WHERE id = %(user_id)s
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, {"user_id": user_id})
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def update(
        self, db_conn: AsyncConnection, user_id: uuid.UUID, data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update user record in db."""
        query = sql.SQL("""
            UPDATE {table}
            SET {set_clause}
            WHERE id = %(user_id)s
            RETURNING *;
        """).format(
            table=sql.Identifier(self.table_name),
            set_clause=build_set_clause(data.keys()),
        )
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, data | {"user_id": user_id})
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_id(
        self, db_conn: AsyncConnection, user_id: uuid.UUID
    ) -> dict[str, Any] | None:
        """Select user record by email from db."""
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE id = %(user_id)s;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, {"user_id": user_id})
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_email(
        self, db_conn: AsyncConnection, email: str
    ) -> dict[str, Any] | None:
        """Select user record by email from db."""
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE email = %(email)s;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, {"email": email})
            return await cur.fetchone()


users_table = UsersTable()
