import logging
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class UsersTable(BaseTable):
    """Users database model."""

    def __init__(self) -> None:
        super().__init__(table="users")

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

            user = await cur.fetchone()
            if user is None:
                raise HTTPException(status_code=404, detail=f"User {id} not found")
            return user
