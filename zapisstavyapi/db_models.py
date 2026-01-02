import uuid

from fastapi import HTTPException
from psycopg import Connection, sql
from psycopg.rows import dict_row

from .models import (
    MeterCreateRequestBody,
    MeterResponseJson,
    MeterUpdateRequestBody,
    ReadingCreateRequestBody,
    ReadingResponseJson,
    ReadingUpdateRequestBody,
)


class MetersTable:
    """Meters database model."""

    @classmethod
    async def select_all(
        cls, conn: Connection, offset: int = 0, limit: int = 100
    ) -> list[MeterResponseJson]:
        """Select all meters records from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM meters
                OFFSET %(offset)s
                LIMIT %(limit)s;
            """)
            await cur.execute(query, {"offset": offset, "limit": limit})
            return await cur.fetchall()

    @classmethod
    async def select_by_id(cls, conn: Connection, id: uuid.UUID) -> MeterResponseJson:
        """Select meter record by ID from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM meters
                WHERE id = %(id)s;
            """)
            await cur.execute(query, {"id": id})

            meter = await cur.fetchone()
            if meter is None:
                raise HTTPException(detail="Meter not found")
            return meter

    @classmethod
    async def insert(
        cls, conn: Connection, meter: MeterCreateRequestBody
    ) -> MeterResponseJson:
        """Insert new meter record into db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = meter.model_dump()
            query = sql.SQL("""
                INSERT INTO meters ({columns})
                VALUES ({value_placeholders})
                RETURNING *;
            """).format(
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                value_placeholders=sql.SQL(", ").join(
                    map(sql.Placeholder, data.keys())
                ),
            )
            await cur.execute(query, data)

            new_meter = await cur.fetchone()
            if new_meter is None:
                raise HTTPException(status_code=500, detail="Meter cannot be created")

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return new_meter

    @classmethod
    async def delete(cls, conn: Connection, id: uuid.UUID) -> None:
        """Delete meter record from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                DELETE FROM meters
                WHERE id = %(id)s;
            """)
            await cur.execute(query, {"id": id})

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    @classmethod
    async def update(
        cls, conn: Connection, id: uuid.UUID, meter: MeterUpdateRequestBody
    ) -> MeterResponseJson:
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
            query = sql.SQL("""
                UPDATE meters
                SET {set_clause}
                WHERE id = %(id)s RETURNING *;
            """).format(
                set_clause=set_clause,
            )
            await cur.execute(query, data | {"id": id})

            updated_meter = await cur.fetchone()
            if updated_meter is None:
                raise HTTPException(status_code=500, detail="Meter cannot be updated")

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return updated_meter


class ReadingsTable:
    """Readings database model."""

    @classmethod
    async def select_by_meter_id(
        cls, conn: Connection, meter_id: uuid.UUID
    ) -> list[ReadingResponseJson]:
        """Select all readings records on a given meter from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                SELECT * FROM readings
                WHERE meter_id = %(meter_id)s;
            """)
            await cur.execute(query, {"meter_id": meter_id})

            return await cur.fetchall()

    @classmethod
    async def insert(
        cls, conn: Connection, reading: ReadingCreateRequestBody
    ) -> ReadingResponseJson:
        """Insert new reading record into db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = reading.model_dump()
            query = sql.SQL("""
                INSERT INTO readings ({columns})
                VALUES ({values})
                RETURNING *;
            """).format(
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                values=sql.SQL(", ").join(map(sql.Placeholder, data.keys())),
            )
            await cur.execute(query, data)

            new_reading = await cur.fetchone()
            if new_reading is None:
                raise HTTPException(status_code=500, detail="Reading cannot be created")
            return new_reading

    @classmethod
    async def delete(cls, conn: Connection, id: uuid.UUID) -> None:
        """Delete reading record from db."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("""
                DELETE FROM readings
                WHERE id = %(id)s;
            """)
            await cur.execute(query, {"id": id})

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    @classmethod
    async def update(
        cls, conn: Connection, id: uuid.UUID, reading: ReadingUpdateRequestBody
    ) -> ReadingResponseJson:
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
            query = sql.SQL("""
                UPDATE readings
                SET {set_clause}
                WHERE id = %(id)s RETURNING *;
            """).format(
                set_clause=set_clause,
            )
            await cur.execute(query, data | {"id": id})

            updated_reading = await cur.fetchone()
            if updated_reading is None:
                raise HTTPException(status_code=500, detail="Meter cannot be updated")

            try:
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

            return updated_reading
