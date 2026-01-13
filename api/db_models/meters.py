import logging
import uuid
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..models.meters import (
    MeterCreateRequestBody,
    MeterUpdateRequestBody,
)
from ..utils import format_sql_query, log_async_func
from .base import BaseTable

logger = logging.getLogger(__name__)


class MetersTable:
    """Meters database model."""

    @classmethod
    @log_async_func(logger.debug)
    async def insert(
        cls, conn: AsyncConnection, meter: MeterCreateRequestBody
    ) -> dict[str, Any]:
        """Insert new meter record into db."""
        return await BaseTable.insert(conn, meter.model_dump(), table="meters")

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete meter record from db."""
        return await BaseTable.delete(conn, id, table="meters")

    @classmethod
    @log_async_func(logger.debug)
    async def update(
        cls, conn: AsyncConnection, id: uuid.UUID, meter: MeterUpdateRequestBody
    ) -> dict[str, Any]:
        """Update meter record in db."""
        data = meter.model_dump()
        data.pop("user_id", None)
        return await BaseTable.update(conn, id, data, table="meters")

    @classmethod
    @log_async_func(logger.debug)
    async def select_by_id(cls, conn: AsyncConnection, id: uuid.UUID) -> dict[str, Any]:
        """Select meter record by ID from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM {table}
                WHERE id = %(id)s;
            """).format(table=sql.Identifier("meters"))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"id": id})

            meter = await cur.fetchone()

            if meter is None:
                raise HTTPException(status_code=404, detail=f"Meter {id} not found")

            return meter
