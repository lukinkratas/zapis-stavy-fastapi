import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Location


async def create_location(
    db_session: AsyncSession, name: str, user_id: str | uuid.UUID
) -> Location:
    location = Location(name=name, user_id=user_id)
    db_session.add(location)

    try:
        await db_session.commit()
    except IntegrityError as e:
        await db_session.rollback()
        raise e

    await db_session.refresh(location)
    return location


async def update_location(
    db_session: AsyncSession,
    location_id: str | uuid.UUID,
    user_id: str | uuid.UUID,
    name: str | None = None,
) -> Location | None:
    result = await db_session.execute(
        select(Location).where(Location.id == location_id, Location.user_id == user_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        return None

    if name:
        setattr(location, "name", name)

    await db_session.commit()
    await db_session.refresh(location)
    return location


async def delete_location(
    db_session: AsyncSession, location_id: str | uuid.UUID, user_id: str | uuid.UUID
) -> bool:
    result = await db_session.execute(
        select(Location).where(Location.id == location_id, Location.user_id == user_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        return False

    await db_session.delete(location)
    await db_session.commit()
    return True
