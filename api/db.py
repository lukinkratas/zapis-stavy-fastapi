import logging
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import Request
from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo

load_dotenv(override=True)
logger = logging.getLogger(__name__)


def get_conn_info() -> str:
    """Return connection info as string for psycopg database connection."""
    return make_conninfo(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", 5432),
    )


async def connect_to_db(request: Request) -> AsyncGenerator[AsyncConnection, None]:
    """Create connection in connection pool."""
    # NOTE: this func cannot decorated, as it is used as endpoint dependency
    async with request.app.state.pool.connection() as conn:
        logger.info(f"New DB connection created. ({str(conn)})")
        yield conn
        logger.info(f"DB connection closed. ({conn})")
