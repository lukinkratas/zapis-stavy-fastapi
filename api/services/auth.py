"""Service layer for handling authentication.

Database transaction is handled in this module.
"""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from .users import select_user_by_id
from ..models import User
from ..utils import log_async_func

logger = logging.getLogger(__name__)


@log_async_func(logger.debug)
async def confirm_user(db_session: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Confirm a user in the database.

    Args:
        db_conn: database connection
        user_id: user id to be confirmed

    Returns: user
    """
    user = await select_user_by_id(db_session, user_id)

    if not user:
        return None

    user.confirmed = True

    await db_session.commit()
    await db_session.refresh(user)
    return user
