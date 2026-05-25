import logging
import os
from typing import AsyncGenerator

from dotenv import load_dotenv

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


logger = logging.getLogger(__name__)
load_dotenv()

class Base(DeclarativeBase):
    pass


db_url = URL.create(
    drivername="postgresql+asyncpg",
    username=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    database=os.environ["DB_NAME"],
)

engine = create_async_engine(
    db_url,
    echo=False,  # set True for SQL logging
    pool_pre_ping=True,  # avoids stale connections
)


# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
