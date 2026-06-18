"""Service layer for handling location lifecycle - create, update and delete.

Database transaction is handled in this module.
"""

import logging
import uuid

from psycopg import AsyncConnection

from ..repositories.locations import LocationRow, locations_table
from ..schemas import CreateProps, UpdateProps
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_by_id(
    db_conn: AsyncConnection, location_id: uuid.UUID
) -> LocationRow | None:
    """Select location from the database by id.

    Args:
        db_conn: database connection
        location_id: id of the location being selected

    Returns: location row
    """
    return await locations_table.select_by_id(db_conn, location_id)


@log_async_func(logger.debug)
async def create(
    db_conn: AsyncConnection, user_id: uuid.UUID, props: CreateProps
) -> LocationRow | None:
    """Add new location into the database.

    Args:
        db_conn: database connection
        user_id: location owner's user id
        props: create location properties request payload from client

    Returns: location row
    """
    async with db_conn.transaction():
        return await locations_table.insert(
            db_conn, user_id, **props.model_dump(exclude_unset=True)
        )


@log_async_func(logger.debug)
async def update(
    db_conn: AsyncConnection,
    location_id: uuid.UUID,
    user_id: uuid.UUID,
    props: UpdateProps,
) -> LocationRow | None:
    """Update a location in the database.

    Args:
        db_conn: database connection
        location_id: location id to be updated
        user_id: location owner's user id
        props: update location properties request payload from client

    Returns: location row
    """
    async with db_conn.transaction():
        return await locations_table.update(
            db_conn, location_id, user_id, props.model_dump(exclude_unset=True)
        )


@log_async_func(logger.debug)
async def delete(
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
