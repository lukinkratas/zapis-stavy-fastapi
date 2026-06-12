import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from psycopg_pool import AsyncConnectionPool
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .db import get_conn_info
from .logging_config import configure_logging
from .routers.auth import router as auth_router
from .routers.locations import router as locations_router
from .routers.users import router as users_router
from .schemas import BaseResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Setup and teardown of the app."""
    configure_logging()
    logger.info("API setup")

    async with AsyncConnectionPool(conninfo=get_conn_info()) as pool:
        app.state.pool = pool
        yield

    # pool = create_connection_pool()
    # app.state.pool = pool
    # await pool.open()

    # yield

    # await pool.close()
    # logger.info("API teardown")


app = FastAPI(
    title="Zapis Stavy FastAPI",
    description="API for Zapis Stavy",
    lifespan=lifespan,
)
app.state.limiter = Limiter(key_func=get_remote_address, default_limits=["1/second"])
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(locations_router)
app.include_router(users_router)
app.include_router(auth_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(
    request: Request, exc: HTTPException
) -> Response:
    """Log error prior to every raise of HTTP exception."""
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


@app.get("/api/v1/health")
async def healthcheck() -> BaseResponse:
    """Check the server is up and running."""
    return BaseResponse(detail="Server is running")
