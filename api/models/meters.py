import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class MetersTable(BaseTable):
    """Meters database model."""

    def __init__(self) -> None:
        super().__init__(table="meters")

    @log_async_func(logger.debug)
    async def select_by_id(
        self, conn: AsyncConnection, id: uuid.UUID, user_id: uuid.UUID
    ) -> dict[str, Any]:
        """Select meter record by ID from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM {table}
                WHERE id = %(id)s AND user_id = %(user_id)s;
            """).format(table=sql.Identifier(self.table))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"id": id, "user_id": user_id})

            return await cur.fetchone()


meters_table = MetersTable()
