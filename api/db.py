import logging
from typing import AsyncGenerator

from fastapi import Request
from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo

from .config import get_db_settings

logger = logging.getLogger(__name__)


def get_conn_info() -> str:
    """Return connection info as string for psycopg database connection."""
    db_settings = get_db_settings()
    return make_conninfo(
        dbname=db_settings.name,
        user=db_settings.username,
        password=db_settings.password,
        host=db_settings.host,
        port=db_settings.port,
    )


# def create_connection_pool() -> AsyncConnectionPool:
#     """Create connection pool."""
#     return AsyncConnectionPool(conninfo=get_conn_info())


async def connect_to_db(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Create connection in connection pool."""
    async with request.app.state.pool.connection() as conn:
        logger.info("New DB connection established.")
        yield conn
        logger.info("DB connection closed.")
