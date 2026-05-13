import logging
import os
from typing import Annotated, Any

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import create_confirmation_token, get_current_user
from ..aws import ses_send_email
from ..db import get_db_session
from ..schemas import BaseResponse, RegisterCreds, ResponseWithId, UpdateCreds
from ..services.users import delete_user, register_user, update_user
from ..utils import log_async_func

ENV = os.getenv("ENV", "dev")

logger = logging.getLogger(__name__)
load_dotenv(override=True)
router = APIRouter(prefix="/v1/user")


def _send_confirmation_email(email: str, confirmation_url: str) -> None:
    """Send email via AWS SES."""
    message = {
        "Subject": {
            "Data": "[Zapis Stavy] Successfully registered - Please confirm your email",
            "Charset": "UTF-8",
        },
        "Body": {
            "Html": {
                "Data": (
                    "<html>"
                    "<body>"
                    "<p>You were successfully registered into Zapis Stavy app.</p>"
                    "<p></p>"
                    "<p>"
                    f"Please "
                    f"<a href='{confirmation_url}'>confirm your email here</a>"
                    "."
                    "</p>"
                    "</body>"
                    "</html>"
                ),
                "Charset": "UTF-8",
            }
        },
    }
    ses_send_email(email, message)


@router.post("/register", status_code=201, response_model=ResponseWithId)
@log_async_func(logger.info)
async def register(
    request: Request,
    creds: RegisterCreds,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Add new user into the database.

    Args:
        request: FastAPI request object (used for accessing headers, client info, etc.).
        user: user create request payload from client
        background_tasks: FastAPI's background que for tasks

    Returns: response with detail and user_id
    """
    try:
        user = await register_user(db_session, **creds.model_dump())
        await db_session.commit()

    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(status_code=409, detail="User already exists")

    response = {
        "detail": "User registered. Please confirm your email.",
        "id": str(user.id),
    }
    confirmation_url = str(
        request.url_for("confirm_user", token=create_confirmation_token(user.id))
    )
    background_tasks.add_task(_send_confirmation_email, user.email, confirmation_url)

    if ENV == "dev":
        response["confirmation_url"] = confirmation_url

    return response


@router.put("", response_model=BaseResponse)
@log_async_func(logger.info)
async def update(
    creds: UpdateCreds,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, str]:
    """Update a meter in the database.

    Args:
        user: user update request payload from client
        current_user: current authorized user

    Returns: response with detail
    """
    try:
        user = await update_user(
            db_session, current_user.id, **creds.model_dump(exclude_unset=True)
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await db_session.commit()

    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(status_code=409, detail="Email already in use")

    return {"detail": "User updated"}


@router.delete("", response_model=BaseResponse)
@log_async_func(logger.info)
async def delete(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a user from the database.

    Args:
        current_user: current authorized user

    Returns: response with detail
    """
    deleted = await delete_user(db_session, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    await db_session.commit()

    return {"detail": "User deleted"}
