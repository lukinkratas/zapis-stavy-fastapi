import logging
import uuid
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..models.readings import (
    ReadingCreateRequestBody,
    ReadingUpdateRequestBody,
)
from ..utils import format_sql_query, log_async_func
from .const import DELETE_QUERY, INSERT_QUERY, UPDATE_QUERY

logger = logging.getLogger(__name__)


class ReadingsTable:
    """Readings database model."""

    @classmethod
    @log_async_func(logger.debug)
    async def insert(
        cls, conn: AsyncConnection, reading: ReadingCreateRequestBody
    ) -> dict[str, Any]:
        """Insert new reading record into db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = reading.model_dump()
            query = INSERT_QUERY.format(
                table=sql.Identifier("readings"),
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                value_placeholders=sql.SQL(", ").join(
                    map(sql.Placeholder, data.keys())
                ),
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data)

            new_reading = await cur.fetchone()
            if new_reading is None:
                raise HTTPException(status_code=404, detail="Reading cannot be created")
            return new_reading

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

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID) -> None:
        """Delete reading record from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = DELETE_QUERY.format(table=sql.Identifier("readings"))
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, {"id": id})

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    @classmethod
    @log_async_func(logger.debug)
    async def update(
        cls, conn: AsyncConnection, id: uuid.UUID, reading: ReadingUpdateRequestBody
    ) -> dict[str, Any]:
        """Update reading record in db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = reading.model_dump()
            data.pop("meter_id", None)

            # build SET clause: col = %(col)s
            set_clause = sql.SQL(", ").join(
                sql.SQL("{columns} = {value_placeholder}").format(
                    columns=sql.Identifier(col),
                    value_placeholder=sql.Placeholder(col),
                )
                for col in data.keys()
            )
            query = UPDATE_QUERY.format(
                table=sql.Identifier("readings"), set_clause=set_clause
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data | {"id": id})

            updated_reading = await cur.fetchone()
            if updated_reading is None:
                raise HTTPException(
                    status_code=404, detail=f"Reading {id} cannot be updated"
                )

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return updated_reading
