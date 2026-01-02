from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool

from .db import get_conn_info
from .logging_config import configure_logging
from .routes import router as meter_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Setup and teardown of the app."""
    configure_logging()
    print("Setup")
    async with AsyncConnectionPool(conninfo=get_conn_info()) as pool:
        app.state.pool = pool
        yield
    print("Teardown")


app = FastAPI(lifespan=lifespan)

app.include_router(meter_router)
