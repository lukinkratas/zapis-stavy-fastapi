"""Service layer for handling location lifecycle - create, update and delete.

Database transaction is handled in this module.
"""

import logging
import uuid
from typing import Any

from psycopg import AsyncConnection

from ..models.locations import LocationRow, locations_table
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_location_by_id(
    db_conn: AsyncConnection, location_id: uuid.UUID
) -> LocationRow | None:
    return await locations_table.select_by_id(db_conn, location_id)


@log_async_func(logger.debug)
async def create_location(
    db_conn: AsyncConnection, user_id: uuid.UUID, name: str
) -> LocationRow | None:
    """Add new location into the database.

    Args:
        db_conn: database connection
        user_id: location owner's user id
        name: name of the location being created

    Returns: location row
    """
    async with db_conn.transaction():
        return await locations_table.insert(db_conn, user_id, name)


@log_async_func(logger.debug)
async def update_location(
    db_conn: AsyncConnection,
    location_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict[str, Any],
) -> LocationRow | None:
    """Update a location in the database.

    Args:
        db_conn: database connection
        location_id: location id to be updated
        user_id: location owner's user id
        data: field-value pairs to be updated

    Returns: location row
    """
    async with db_conn.transaction():
        return await locations_table.update(db_conn, location_id, user_id, data)


@log_async_func(logger.debug)
async def delete_location(
    db_conn: AsyncConnection, location_id: uuid.UUID, user_id: uuid.UUID
) -> LocationRow | None:
    """Delete a location from the database.

    Args:
        db_conn: database connection
        location_id: location id to be updated
        user_id: location owner's user id

    Returns: location row
    """
    async with db_conn.transaction():
        return await locations_table.delete(db_conn, location_id, user_id)
