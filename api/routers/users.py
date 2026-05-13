import logging
import os
from typing import Annotated, Any

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation

from ..auth import create_confirmation_token, get_current_user
from ..aws import ses_send_email
from ..db import connect_to_db
from ..exceptions import user_exists_exception, user_not_found_exception
from ..schemas import BaseResponse, RegisterCreds, ResponseWithId, UpdateCreds
from ..services.users import delete_user, register_user, update_user

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
                    "Please "
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
async def register(
    request: Request,
    creds: RegisterCreds,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
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
        user = await register_user(db_conn, **creds.model_dump())

    except UniqueViolation:
        raise user_exists_exception

    response = {
        "detail": "User registered. Please confirm your email.",
        "id": user["id"],
    }
    confirmation_token = create_confirmation_token(user["id"])
    background_tasks.add_task(
        _send_confirmation_email,
        user["email"],
        confirmation_url=str(request.url_for("confirm", token=confirmation_token)),
    )

    if ENV == "dev":
        response["confirmation_token"] = confirmation_token

    return response


@router.put("", response_model=BaseResponse)
async def update(
    creds: UpdateCreds,
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
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
            db_conn, current_user["id"], creds.model_dump(exclude_unset=True)
        )

        if not user:
            raise user_not_found_exception

    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already in use")

    return {"detail": "User updated"}


@router.delete("", response_model=BaseResponse)
async def delete(
    db_conn: Annotated[AsyncConnection, Depends(connect_to_db)],
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a user from the database.

    Args:
        current_user: current authorized user

    Returns: response with detail
    """
    user = await delete_user(db_conn, current_user["id"])

    if not user:
        raise user_not_found_exception

    return {"detail": "User deleted"}
