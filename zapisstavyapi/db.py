import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import Request
from psycopg import Connection
from psycopg.conninfo import make_conninfo


def get_conn_info() -> str:
    """Return connection info as string for psycopg database connection."""
    load_dotenv(override=True)

    conn_info_dict = dict(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", 5432),
    )
    return make_conninfo(**conn_info_dict)


async def db_connect(request: Request) -> AsyncGenerator[Connection, None]:
    """Create connection in connection pool."""
    async with request.app.state.pool.connection() as conn:
        yield conn
