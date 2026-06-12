import uuid
from datetime import timedelta
from typing import Callable, Literal

import jwt
import pytest
from fastapi import HTTPException

from api.auth import (
    _create_jwt_token,
    create_access_token,
    create_confirmation_token,
    get_sub,
)
from api.config import JwtSettings, get_jwt_settings


@pytest.fixture
def jwt_settings() -> JwtSettings:
    return get_jwt_settings()


@pytest.mark.asyncio
async def test_create_jwt_token(jwt_settings: JwtSettings) -> None:
    token = _create_jwt_token({"random": "random"}, expires_delta=timedelta(minutes=1))
    decoded_token = jwt.decode(
        token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm]
    )
    assert decoded_token["random"] == "random"


@pytest.mark.asyncio
async def test_create_access_token(jwt_settings: JwtSettings) -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    decoded_token = jwt.decode(
        token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm]
    )
    assert decoded_token["sub"] == str(user_id)
    assert decoded_token["type"] == "access"


@pytest.mark.asyncio
async def test_create_confirmation_token(jwt_settings: JwtSettings) -> None:
    user_id = uuid.uuid4()
    token = create_confirmation_token(user_id)
    decoded_token = jwt.decode(
        token, key=jwt_settings.secret_key, algorithms=[jwt_settings.algorithm]
    )
    assert decoded_token["sub"] == str(user_id)
    assert decoded_token["type"] == "confirmation"


@pytest.mark.parametrize(
    ("typ", "create_token_func"),
    [
        pytest.param("access", create_access_token, id="access"),
        pytest.param("confirmation", create_confirmation_token, id="confirmation"),
    ],
)
def test_get_sub(
    typ: Literal["access", "confirmation"],
    create_token_func: Callable[[uuid.UUID], str],
) -> None:
    user_id = uuid.uuid4()
    token = create_token_func(user_id)
    assert get_sub(token, typ) == str(user_id)


def test_get_sub_invalid() -> None:
    token = "invalid"
    with pytest.raises(HTTPException):
        get_sub(token, typ="access")


def test_get_sub_wrong_type() -> None:
    user_id = uuid.uuid4()
    token = create_confirmation_token(user_id)
    with pytest.raises(HTTPException):
        get_sub(token, typ="access")


def test_get_sub_expired_token() -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id, expires_delta=timedelta(-1))
    with pytest.raises(HTTPException):
        get_sub(token, typ="access")


def test_get_sub_missing_sub() -> None:
    token = _create_jwt_token({"type": "access"}, timedelta(minutes=15))
    with pytest.raises(HTTPException):
        get_sub(token, typ="access")
