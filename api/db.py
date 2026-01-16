import logging
from typing import AsyncGenerator

from fastapi import Request
from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo

from .config import Settings

logger = logging.getLogger(__name__)


def get_conn_info(settings: Settings) -> str:
    """Return connection info as string for psycopg database connection."""
    conn_info_dict = dict(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
    )
    return make_conninfo(**conn_info_dict)


async def connect_to_db(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Create connection in connection pool."""
    # NOTE: this func cannot decorated, as it is used as endpoint dependency
    async with request.app.state.pool.connection() as conn:
        logger.info(f"New DB connection created. ({str(conn)})")
        yield conn
        logger.info(f"DB connection closed. ({conn})")
