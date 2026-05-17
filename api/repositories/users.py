"""Database tables layer for handling users lifecycle - insert, update and delete."""

import logging
import uuid
from datetime import datetime
from typing import Any, NamedTuple

from psycopg import AsyncConnection, sql
from psycopg.rows import class_row

from ..utils import build_set_clause, format_sql_query, log_async_func

logger = logging.getLogger(__name__)


class UserRow(NamedTuple):
    id: uuid.UUID
    created_at: datetime
    email: str
    password_hash: str
    confirmed: bool


class UsersTable:
    """User database model."""

    def __init__(self) -> None:
        self.table_name = "users"

    @log_async_func(logger.debug)
    async def insert(
        self, db_conn: AsyncConnection, email: str, password_hash: str
    ) -> UserRow | None:
        """Insert new user record into db.

        Args:
            db_conn: database connection
            email: email of the user being inserted
            password_hash: hashed password of the user being registered

        Returns: user row
        """
        query = sql.SQL("""
            INSERT INTO {table} (email, password_hash)
            VALUES (%(email)s, %(password_hash)s)
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(UserRow)) as cur:
            await cur.execute(query, dict(email=email, password_hash=password_hash))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def update(
        self, db_conn: AsyncConnection, user_id: uuid.UUID, data: dict[str, Any]
    ) -> UserRow | None:
        """Update user record in db.

        Args:
            db_conn: database connection
            user_id: user id to be updated
            data: field-value pairs to be updated

        Returns: user row
        """
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

        async with db_conn.cursor(row_factory=class_row(UserRow)) as cur:
            await cur.execute(query, data | dict(user_id=user_id))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def delete(
        self, db_conn: AsyncConnection, user_id: uuid.UUID
    ) -> UserRow | None:
        """Delete user record from db.

        Args:
            db_conn: database connection
            user_id: user id to be deleted

        Returns: user row
        """
        query = sql.SQL("""
            DELETE FROM {table}
            WHERE id = %(user_id)s
            RETURNING *;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(UserRow)) as cur:
            await cur.execute(query, dict(user_id=user_id))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_id(
        self, db_conn: AsyncConnection, user_id: uuid.UUID
    ) -> UserRow | None:
        """Select user record from db filtered by id.

        Args:
            db_conn: database connection
            user_id: user id to be selected

        Returns: user row
        """
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE id = %(user_id)s;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(UserRow)) as cur:
            await cur.execute(query, dict(user_id=user_id))
            return await cur.fetchone()

    @log_async_func(logger.debug)
    async def select_by_email(
        self, db_conn: AsyncConnection, email: str
    ) -> UserRow | None:
        """Select user record from db filtered by email.

        Args:
            db_conn: database connection
            email: email of the user being selected

        Returns: user row
        """
        query = sql.SQL("""
            SELECT * FROM {table}
            WHERE email = %(email)s;
        """).format(table=sql.Identifier(self.table_name))
        logger.debug(f"SQL query: {format_sql_query(query)}")

        async with db_conn.cursor(row_factory=class_row(UserRow)) as cur:
            await cur.execute(query, dict(email=email))
            return await cur.fetchone()


users_table = UsersTable()
