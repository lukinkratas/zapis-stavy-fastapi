"""Service layer for handling location lifecycle - create, update and delete.

Database transaction is handled in this module.
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Location
from ..schemas import CreateProps, UpdateProps
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_location_by_id(
    db_session: AsyncSession, location_id: uuid.UUID
) -> Location | None:
    """Select location from the database by id.

    Args:
        db_conn: database connection
        location_id: id of the location being selected

    Returns: location
    """
    result = await db_session.execute(select(Location).where(Location.id == location_id))
    return result.scalar_one_or_none()


@log_async_func(logger.debug)
async def create_location(
    db_session: AsyncSession, user_id: uuid.UUID, props: CreateProps
) -> Location | None:
    """Add new location into the database.

    Args:
        db_conn: database connection
        user_id: location owner's user id
        props: create location properties request payload from client

    Returns: location
    """
    location = Location(**props.model_dump(exclude_unset=True))
    db_session.add(location)

    try:
        await db_session.commit()
    except IntegrityError as e:
        await db_session.rollback()
        raise e

    await db_session.refresh(location)
    return location


@log_async_func(logger.debug)
async def update_location(
    db_session: AsyncSession,
    location_id: uuid.UUID,
    user_id: uuid.UUID,
    props: UpdateProps,
) -> Location | None:
    """Update a location in the database.

    Args:
        db_conn: database connection
        location_id: location id to be updated
        user_id: location owner's user id
        props: update location properties request payload from client

    Returns: location
    """
    data = props.model_dump(exclude_unset=True)
    result = await db_session.execute(
        select(Location).where(Location.id == location_id, Location.user_id == user_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        return None

    if "name" in data:
        location.name = data["name"]

    await db_session.commit()
    await db_session.refresh(location)
    return location


@log_async_func(logger.debug)
async def delete_location(
    db_session: AsyncSession, location_id: uuid.UUID, user_id: uuid.UUID
) -> Location | None:
    """Delete a location from the database.

    Args:
        db_conn: database connection
        location_id: location id to be updated
        user_id: location owner's user id

    Returns: location
    """    
    result = await db_session.execute(
        select(Location).where(Location.id == location_id, Location.user_id == user_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        return False

    await db_session.delete(location)
    await db_session.commit()
    return True
