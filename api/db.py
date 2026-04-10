import logging
from typing import AsyncGenerator

from fastapi import Request
from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo

from .config import Settings

logger = logging.getLogger(__name__)


def get_conn_info(settings: Settings) -> str:
    """Return connection info as string for psycopg database connection."""
    return make_conninfo(
        dbname=settings.DB_NAME,
        user=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )


async def connect_to_db(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Create connection in connection pool."""
    # NOTE: this func cannot decorated, as it is used as endpoint dependency
    async with request.app.state.pool.connection() as conn:
        logger.info(f"New DB connection created. ({str(conn)})")
        yield conn
        logger.info(f"DB connection closed. ({conn})")
