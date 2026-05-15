"""Service layer for handling authentication.

Database transaction is handled in this module.
"""

import logging
import uuid

from psycopg import AsyncConnection

from ..models.users import UserRow, users_table
from ..utils import log_async_func

logger = logging.getLogger(__name__)

@log_async_func(logger.debug)
async def confirm_user(db_conn: AsyncConnection, user_id: uuid.UUID) -> UserRow | None:
    """Confirm a user in the database.

    Args:
        db_conn: database connection
        user_id: user id to be confirmed

    Returns: user row
    """
    async with db_conn.transaction():
        return await users_table.update(db_conn, user_id, {"confirmed": True})
