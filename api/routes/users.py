import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from psycopg import Connection

from ..db import connect_to_db
from ..db_models.users import UsersTable
from ..models.users import UserCreateRequestBody, UserResponseJson
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", status_code=201, response_model=UserResponseJson)
@log_async_func(logger.info)
async def create_user(
    user: UserCreateRequestBody, conn: Annotated[Connection, Depends(connect_to_db)]
) -> UserResponseJson:
    """Add new user into the database.

    Args:
        user: user create request payload from client
        conn: database connection

    Returns: user response dict
    """
    return await UsersTable.insert(conn, user)
