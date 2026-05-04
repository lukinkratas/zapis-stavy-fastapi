import uuid
from psycopg import AsyncConnection
from ..models.users import locations_table
from typing import Any

async def create_location(conn: AsyncConnection, user_id: str | uuid.UUID, data: dict[str, Any]):
    return await locations_table.insert(conn, user_id, data)

async def update_location(conn: AsyncConnection, location_id: str | uuid.UUID, user_id: str | uuid.UUID, data: dict[str, Any]):
    await locations_table.update(conn, location_id, user_id, data)

async def delete_location(conn: AsyncConnection, location_id: str | uuid.UUID, user_id: str | uuid.UUID):
    await locations_table.delete(conn, location_id, user_id)