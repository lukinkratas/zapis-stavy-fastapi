import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import Response
from psycopg_pool import AsyncConnectionPool

from .config import Settings
from .db import get_conn_info
from .logging_config import configure_logging
from .routes.meters import router as meters_router
from .routes.readings import router as readings_router
from .routes.users import router as users_router

logger = logging.getLogger(__name__)


@lru_cache
def get_settings() -> Settings:
    """Load Postgres ans FastAPI config."""
    return Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Setup and teardown of the app."""
    settings = get_settings()
    configure_logging(settings)
    logger.info("Setup")

    async with AsyncConnectionPool(conninfo=get_conn_info(settings)) as pool:
        app.state.pool = pool
        yield

    logger.info("Teardown")


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(meters_router)
app.include_router(readings_router)
app.include_router(users_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(
    request: Request, exc: HTTPException
) -> Response:
    """Log error prior to every raise of HTTP exception."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
