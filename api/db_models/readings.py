import logging
import uuid
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..models.readings import (
    ReadingCreateRequestBody,
    ReadingUpdateRequestBody,
)
from ..utils import format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class ReadingsTable:
    """Readings database model."""

    @classmethod
    @log_async_func(logger.debug)
    async def insert(
        cls, conn: AsyncConnection, reading: ReadingCreateRequestBody
    ) -> dict[str, Any]:
        """Insert new reading record into db."""
        return await BaseTable.insert(conn, data=reading.model_dump(), table="readings")

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete reading record from db."""
        return await BaseTable.delete(conn, id, table="readings")

    @classmethod
    @log_async_func(logger.debug)
    async def update(
        cls, conn: AsyncConnection, id: uuid.UUID, reading: ReadingUpdateRequestBody
    ) -> dict[str, Any]:
        """Update reading record in db."""
        data = reading.model_dump()
        data.pop("meter_id", None)
        return await BaseTable.update(conn, id, data, table="readings")

    @classmethod
    @log_async_func(logger.debug)
    async def select_by_meter_id(
        cls,
        conn: AsyncConnection,
        meter_id: uuid.UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Select all readings records on a given meter from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM readings
                WHERE meter_id = %(meter_id)s
                OFFSET %(offset)s
                LIMIT %(limit)s;
            """)
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(
                query, {"meter_id": meter_id, "offset": offset, "limit": limit}
            )

            return await cur.fetchall()
