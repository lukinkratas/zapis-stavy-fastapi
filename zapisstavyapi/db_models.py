import uuid
from typing import NoReturn

from fastapi import HTTPException
from psycopg import Connection, sql
from psycopg.rows import dict_row

from .models import MeterReq, MeterResp, ReadingReq, ReadingResp


class MetersTable:
    """Meters database model."""

    @classmethod
    async def retrieve_all(
        cls, conn: Connection, offset: int = 0, limit: int = 100
    ) -> list[MeterResp]:
        """Get all meters from meters table."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("SELECT * FROM meters OFFSET %(offset)s LIMIT %(limit)s;")
            await cur.execute(query, {"offset": offset, "limit": limit})
            return await cur.fetchall()

    @classmethod
    async def retrieve_by_id(
        cls, conn: Connection, id: uuid.UUID
    ) -> MeterResp | NoReturn:
        """Get meter from meters table by ID."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("SELECT * FROM meters WHERE id = %(id)s;")
            await cur.execute(query, {"id": id})

            meter = await cur.fetchone()
            if meter is None:
                raise HTTPException("Meter not found.")
            return meter

    @classmethod
    async def create(cls, conn: Connection, meter: MeterReq) -> MeterResp | NoReturn:
        """Creater new meter record in meters table."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = meter.model_dump()
            query = sql.SQL(
                "INSERT INTO meters ({columns}) VALUES ({values}) RETURNING *;"
            ).format(
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                values=sql.SQL(", ").join(map(sql.Placeholder, data.keys())),
            )
            await cur.execute(query, data)

            new_meter = await cur.fetchone()
            if new_meter is None:
                raise HTTPException("Meter cannot be created", status_code=500)
            return new_meter


class ReadingsTable:
    """Readings database model."""

    @classmethod
    async def retrieve_by_meter_id(
        cls, conn: Connection, meter_id: uuid.UUID
    ) -> list[ReadingResp]:
        """Get all readings on meter from readings table."""
        async with conn.cursor(row_factory=dict_row) as cur:
            query = sql.SQL("SELECT * FROM readings WHERE meter_id = %(meter_id)s;")
            await cur.execute(query, {"meter_id": meter_id})

            return await cur.fetchall()

    @classmethod
    async def create(
        cls, conn: Connection, reading: ReadingReq
    ) -> ReadingResp | NoReturn:
        """Create new reading record in readings table."""
        async with conn.cursor(row_factory=dict_row) as cur:
            data = reading.model_dump()
            query = sql.SQL(
                "INSERT INTO readings ({columns}) VALUES ({values}) RETURNING *;"
            ).format(
                columns=sql.SQL(", ").join(map(sql.Identifier, data.keys())),
                values=sql.SQL(", ").join(map(sql.Placeholder, data.keys())),
            )
            await cur.execute(query, data)

            new_reading = await cur.fetchone()
            if new_reading is None:
                raise HTTPException("Reading cannot be created.", status_code=500)
            return new_reading
