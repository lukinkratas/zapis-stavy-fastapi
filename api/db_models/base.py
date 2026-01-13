import logging
import uuid
from typing import Any

from fastapi import HTTPException
from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row

from ..utils import build_set_clause, format_sql_query, log_async_func

logger = logging.getLogger(__name__)


class BaseTable:
    """General database model."""

    @classmethod
    async def insert(
        cls, conn: AsyncConnection, data: dict[str, Any], table: str
    ) -> dict[str, Any]:
        """Insert new record into db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                INSERT INTO {table} ({columns})
                VALUES ({value_placeholders})
                RETURNING *;
            """).format(
                table=sql.Identifier(table),
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                value_placeholders=sql.SQL(", ").join(
                    map(sql.Placeholder, data.keys())
                ),
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data)

            new_entity = await cur.fetchone()

            if new_entity is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cannot insert entity {data} into {table} table",
                )

            return new_entity

    @classmethod
    @log_async_func(logger.debug)
    async def delete(cls, conn: AsyncConnection, id: uuid.UUID, table: str) -> None:
        """Delete record from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                DELETE FROM {table}
                WHERE id = %(id)s;
            """).format(table=sql.Identifier(table))
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
        cls, conn: AsyncConnection, id: uuid.UUID, data: dict[str, Any], table: str
    ) -> dict[str, Any]:
        """Update record in db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                UPDATE {table}
                SET {set_clause}
                WHERE id = %(id)s RETURNING *;
            """).format(
                table=sql.Identifier(table),
                set_clause=build_set_clause(data.keys()),
            )
            logger.debug(f"SQL query: {format_sql_query(query)}")
            await cur.execute(query, data | {"id": id})

            updated_entity = await cur.fetchone()

            if updated_entity is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cannot update entity {data} from {table} table",
                )

            try:
                await conn.commit()

            except Exception:
                await conn.rollback()
                raise

            return updated_entity
