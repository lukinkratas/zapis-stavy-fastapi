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
from .const import (
    DELETE_QUERY,
    INSERT_QUERY,
    SELECT_BY_ID_QUERY,
    UPDATE_QUERY,
)

logger = logging.getLogger(__name__)


class MetersTable:
    """Meters database model."""

    @classmethod
    @log_async_func(logger.debug)
    async def insert(
        cls, conn: AsyncConnection, meter: MeterCreateRequestBody
    ) -> dict[str, Any]:
        """Insert new meter record into db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = meter.model_dump()
            query = INSERT_QUERY.format(
                table=sql.Identifier("meters"),
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                value_placeholders=sql.SQL(", ").join(
                    map(sql.Placeholder, data.keys())
                ),
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data)

            new_meter = await cur.fetchone()

            if new_meter is None:
                raise HTTPException(status_code=404, detail="Meter cannot be created")

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return new_meter

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete meter record from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = DELETE_QUERY.format(table=sql.Identifier("meters"))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"id": id})

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    @classmethod
    @log_async_func(logger.debug)
    async def select_by_id(cls, conn: AsyncConnection, id: uuid.UUID) -> dict[str, Any]:
        """Select meter record by ID from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = SELECT_BY_ID_QUERY.format(table=sql.Identifier("meters"))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"id": id})

            meter = await cur.fetchone()
            if meter is None:
                raise HTTPException(status_code=404, detail=f"Meter {id} not found")
            return meter

    @classmethod
    @log_async_func(logger.debug)
    async def update(
        cls, conn: AsyncConnection, id: uuid.UUID, meter: MeterUpdateRequestBody
    ) -> dict[str, Any]:
        """Update meter record in db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = meter.model_dump()

            # build SET clause: col = %(col)s
            set_clause = sql.SQL(", ").join(
                sql.SQL("{columns} = {value_placeholder}").format(
                    columns=sql.Identifier(col),
                    value_placeholder=sql.Placeholder(col),
                )
                for col in data.keys()
            )
            query = UPDATE_QUERY.format(
                table=sql.Identifier("meters"), set_clause=set_clause
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data | {"id": id})

            updated_meter = await cur.fetchone()
            if updated_meter is None:
                raise HTTPException(
                    status_code=404, detail=f"Meter {id} cannot be updated"
                )

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return updated_meter
