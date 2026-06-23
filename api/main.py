import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .config import get_settings
from .db import create_connection_pool
from .logging_config import configure_logging
from .routers.auth import router as auth_router
from .routers.locations import router as locations_router
from .routers.users import router as users_router
from .schemas import BaseResponse

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Setup and teardown of the app."""
    configure_logging()
    logger.info("API setup")

    app.state.limiter = Limiter(
        key_func=get_remote_address, default_limits=["1/second"]
    )

    async with create_connection_pool() as pool:
        app.state.pool = pool
        yield

    logger.info("API teardown")


doc_kwargs: dict[str, Any] = (
    dict(docs_url=None, redoc_url=None, openapi_url=None)
    if settings.env == "prod"
    else {}
)
app = FastAPI(
    title="Zapis Stavy",
    description="API for Zapis Stavy",
    version="0.1.0",
    lifespan=lifespan,
    **doc_kwargs,
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zapis-stavy.cz"]
    if settings.env == "prod"
    else ["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
