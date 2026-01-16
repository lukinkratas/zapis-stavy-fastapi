import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class ReadingsTable(BaseTable):
    """Readings database model."""

    def __init__(self) -> None:
        super().__init__(table="readings")

    @log_async_func(logger.debug)
    async def select_by_meter_id(
        self,
        conn: AsyncConnection,
        meter_id: uuid.UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Select all readings records on a given meter from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM {table}
                WHERE meter_id = %(meter_id)s
                OFFSET %(offset)s
                LIMIT %(limit)s;
            """).format(table=sql.Identifier(self.table))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(
                query, {"meter_id": meter_id, "offset": offset, "limit": limit}
            )

            return await cur.fetchall()


readings_table = ReadingsTable()
