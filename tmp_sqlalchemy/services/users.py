import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..security import get_password_hash


async def select_user_by_id(
    db_session: AsyncSession, user_id: str | uuid.UUID
) -> User | None:
    result = await db_session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def select_user_by_email(db_session: AsyncSession, email: str) -> User | None:
    result = await db_session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db_session: AsyncSession, email: str, password: str) -> User:
    user = User(email=email, password=get_password_hash(password))
    db_session.add(user)

    await db_session.flush()
    await db_session.refresh(user)
    return user


async def update_user(
    db_session: AsyncSession,
    user_id: str | uuid.UUID,
    email: str | None = None,
    password: str | None = None,
) -> User | None:
    user = await select_user_by_id(db_session, user_id)

    if not user:
        return None

    if email:
        user.email = email

    if password:
        user.password = get_password_hash(password)

    await db_session.flush()
    await db_session.refresh(user)
    return user


async def delete_user(db_session: AsyncSession, user_id: str | uuid.UUID) -> bool:
    result = await db_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return False

    await db_session.delete(user)
    await db_session.flush()
    return True


async def confirm_user(
    db_session: AsyncSession, user_id: str | uuid.UUID
) -> User | None:
    user = await select_user_by_id(db_session, user_id)

    if not user:
        return None

    user.confirmed = True

    await db_session.commit()
    await db_session.refresh(user)
    return user
