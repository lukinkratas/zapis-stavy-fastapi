import uuid
from datetime import timedelta
from typing import Any, Callable, Literal

import jwt
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.routers.auth import (
    ALGORITHM,
    SECRET_KEY,
    _create_jwt_token,
    create_access_token,
    create_confirmation_token,
    get_sub,
    verify_password,
)
from api.schemas.auth import Token


class TestLogin:
    """Integration tests for login endpoint."""

    @pytest.mark.anyio
    async def test_login_registered_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        data = {
            "username": credentials["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post("/token", data=data)
        assert response.status_code == 200

        token = response.json()
        assert Token.model_validate(token)


class TestConfirm:
    """Integration tests for confirm endpoint."""

    @pytest.mark.anyio
    async def test_confirm_registered_user(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        registered_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        response = await async_client.get(f"/confirm/{confirmation_token}")
        assert response.status_code == 200


class TestOther:
    """Integration tests for other auth helper and private functions."""

    @pytest.mark.anyio
    async def test_verify_password(
        self, credentials: dict[str, str], registered_user: dict[str, Any]
    ) -> None:
        verify_password(credentials["password"], registered_user["password"])

    @pytest.mark.anyio
    async def test_create_access_token(self) -> None:
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == str(user_id)
        assert decoded_token["type"] == "access"

    @pytest.mark.anyio
    async def test_create_confirmation_token(self) -> None:
        user_id = uuid.uuid4()
        token = create_confirmation_token(user_id)
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
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
        self,
        typ: Literal["access", "confirmation"],
        create_token_func: Callable[[uuid.UUID], str],
    ) -> None:
        user_id = uuid.uuid4()
        token = create_token_func(user_id)
        assert get_sub(token, typ=typ) == str(user_id)

    def test_get_sub_invalid(self) -> None:
        token = "invalid"
        with pytest.raises(HTTPException):
            get_sub(token, typ="access")

    def test_get_sub_wrong_type(self) -> None:
        user_id = uuid.uuid4()
        token = create_confirmation_token(user_id)
        with pytest.raises(HTTPException):
            get_sub(token, typ="access")

    def test_get_sub_expired_token(self) -> None:
        user_id = uuid.uuid4()
        token = create_access_token(user_id, expires_delta=timedelta(-1))
        with pytest.raises(HTTPException):
            get_sub(token, typ="access")

    def test_get_sub_missing_sub(self) -> None:
        token = _create_jwt_token({"type": "access"}, timedelta(minutes=15))
        with pytest.raises(HTTPException):
            get_sub(token, typ="access")
