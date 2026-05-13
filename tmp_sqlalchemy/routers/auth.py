import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import authenticate_user, create_access_token, get_sub, token_exception
from ..db import get_db_session
from ..exceptions import token_exception
from ..schemas import Token
from ..services.users import confirm_user, select_user_by_id
from ..utils import log_async_func

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/auth")


@router.post("/token", response_model=Token)
@log_async_func(logger.info)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Token:
    """Authenticate user.

    Args:
        form_data: form data with credentials from client
        db_session: database db_sessionection

    Returns: access token

    Raises:
        HTTPException: if user not found in the database or password mismatch.
    """
    user = await authenticate_user(db_session, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user["id"]), token_type="bearer")


@router.get("/confirm/{token}")
@log_async_func(logger.info)
async def confirm(
    token: str, db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict[str, str]:
    """Update user to confirmed = True based on email from token.

    Args:
        token: encoded JWT token
        db_session: database db_sessionection

    Returns: dict with detail message
    """
    user_id = get_sub(token, typ="confirmation")
    # check user exists
    user = await select_user_by_id(db_session, user_id)

    if user is None:
        raise token_exception

    await confirm_user(db_session, user_id)
    return {"detail": "User confirmed."}
