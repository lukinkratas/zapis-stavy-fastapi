from typing import Any
from unittest.mock import AsyncMock

import jwt
import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.users import UsersTable
from api.routers.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_confirmation_token,
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
    async def test_create_access_token(
        self,
        credentials: dict[str, str],
    ) -> None:
        token = create_access_token(credentials["email"])
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == credentials["email"]
        assert decoded_token["type"] == "access"

    @pytest.mark.anyio
    async def test_create_confirmation_token(
        self,
        credentials: dict[str, str],
    ) -> None:
        token = create_confirmation_token(credentials["email"])
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded_token["sub"] == credentials["email"]
        assert decoded_token["type"] == "confirmation"

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
