from datetime import timedelta
from typing import Any
from unittest.mock import AsyncMock

import jwt
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.users import UsersTable
from api.routers.auth import (
    ALGORITHM,
    SECRET_KEY,
    _create_jwt_token,
    create_access_token,
    create_confirmation_token,
    get_subject,
    verify_password,
)
from tests.assertions import assert_token


class TestUnitAuth:
    """Unit tests for auth."""

    @pytest.mark.anyio
    async def test_verify_password(
        self,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        verify_password(credentials["password"], registered_user["password"])

    @pytest.mark.anyio
    async def test_create_access_token(self) -> None:
        email = "test@test.net"
        token = create_access_token(email)
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == email
        assert decoded_token["type"] == "access"

    @pytest.mark.anyio
    async def test_create_confirmation_token(self) -> None:
        email = "test@test.net"
        token = create_confirmation_token(email)
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == email
        assert decoded_token["type"] == "confirmation"

    def test_get_subject_access_token(self) -> None:
        email = "test@test.net"
        token = create_access_token(email)
        assert email == get_subject(token, typ="access")

    def test_get_subject_confirmation_token(self) -> None:
        email = "test@test.net"
        token = create_confirmation_token(email)
        assert email == get_subject(token, typ="confirmation")

    def test_get_subject_invalid(self) -> None:
        token = "invalid"
        with pytest.raises(HTTPException):
            get_subject(token, typ="access")

    def test_get_subject_wrong_type(self) -> None:
        email = "test@test.net"
        token = create_confirmation_token(email)
        with pytest.raises(HTTPException):
            get_subject(token, typ="access")

    def test_get_subject_expired_token(self) -> None:
        email = "test@test.net"
        token = _create_jwt_token({"type": "access", "sub": email}, timedelta(-1))
        with pytest.raises(HTTPException):
            get_subject(token, typ="access")

    def test_get_subject_missing_sub(self) -> None:
        token = _create_jwt_token({"type": "access"}, timedelta(minutes=15))
        with pytest.raises(HTTPException):
            get_subject(token, typ="access")

    @pytest.mark.anyio
    async def test_login(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # mocking - returns user from db with hashed password
        mocker.patch.object(
            UsersTable,
            "select_by_email",
            new=AsyncMock(return_value=registered_user),
        )

        data = {
            "username": credentials["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post("/token", data=data)
        assert response.status_code == 200

        token = response.json()
        assert_token(token)
