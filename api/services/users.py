"""Service layer for handling users lifecycle - register, update and delete.

Database transaction is handled in this module.
"""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import User
from ..schemas import RegisterCreds, UpdateCreds
from ..security import get_password_hash
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def select_user_by_id(
    db_session: AsyncSession, user_id: uuid.UUID
) -> User | None:
    """Select user from the database by id.

    Args:
        db_conn: database connection
        user_id: id of the user being selected

    Returns: user
    """
    result = await db_session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


@log_async_func(logger.debug)
async def select_user_by_email(db_session: AsyncSession, email: str) -> User | None:
    """Select user from the database by email.

    Args:
        db_conn: database connection
        email: email of the user being selected

    Returns: user
    """
    result = await db_session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@log_async_func(logger.debug)
async def register_user(
    db_session: AsyncSession, creds: RegisterCreds
) -> User | None:
    """Add new user into the database.

    Args:
        db_conn: database connection
        creds: register credentials payload from router

    Returns: user
    """
    data = creds.model_dump(exclude_unset=True)
    password = data.pop("password")
    data["password_hash"] = get_password_hash(password)
    
    user = User(**data)
    db_session.add(user)

    await db_session.flush()
    await db_session.refresh(user)
    return user


@log_async_func(logger.debug)
async def update_user(
    db_session: AsyncSession, user_id: uuid.UUID, creds: UpdateCreds
) -> User | None:
    """Update a user in the database.

    Args:
        db_conn: database connection
        user_id: user id to be updated
        creds: credentials update payload from router

    Returns: user
    """
    data = creds.model_dump(exclude_unset=True)
    
    user = await select_user_by_id(db_session, user_id)

    if not user:
        return None

    if "email" in data:
        user.email = data["email"]

    if "password" in data:
        user.password = get_password_hash(data["password"])

    await db_session.flush()
    await db_session.refresh(user)
    return user


@log_async_func(logger.debug)
async def delete_user(db_session: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Delete a user from the database.

    Args:
        db_conn: database connection
        user_id: user id to be updated

    Returns: user
    """
    result = await db_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return False

    await db_session.delete(user)
    await db_session.flush()
    return True