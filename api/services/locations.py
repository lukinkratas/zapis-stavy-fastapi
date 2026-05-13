import logging
import uuid
from typing import Any

from psycopg import AsyncConnection

from ..models.locations import locations_table
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_location_by_id(
    db_conn: AsyncConnection, location_id: uuid.UUID
) -> dict[str, Any] | None:
    return await locations_table.select_by_id(db_conn, location_id)


@log_async_func(logger.debug)
async def create_location(
    db_conn: AsyncConnection, user_id: uuid.UUID, name: str
) -> dict[str, Any]:
    async with db_conn.transaction():
        return await locations_table.insert(db_conn, user_id, name)


@log_async_func(logger.debug)
async def update_location(
    db_conn: AsyncConnection,
    location_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict[str, Any],
) -> dict[str, Any]:
    async with db_conn.transaction():
        return await locations_table.update(db_conn, location_id, user_id, data)


@log_async_func(logger.debug)
async def delete_location(
    db_conn: AsyncConnection, location_id: uuid.UUID, user_id: uuid.UUID
) -> dict[str, Any]:
    async with db_conn.transaction():
        return await locations_table.delete(db_conn, location_id, user_id)
