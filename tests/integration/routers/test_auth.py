from typing import Any, AsyncGenerator

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.config import settings
from api.db import get_conn_info
from api.routers.auth import credentials_exception, get_user
from tests.assertions import assert_token, assert_user


class TestIntegrationAuth:
    """Integration tests for auth."""

    def assert_invalid_token(self, token: dict[str, Any]) -> None:
        assert credentials_exception.detail in token["detail"]
        assert "access_token" not in token.keys()

    @pytest.fixture
    async def conn(self) -> AsyncGenerator[AsyncConnection, None]:
        async with await AsyncConnection.connect(
            conninfo=get_conn_info(settings)
        ) as conn:
            yield conn

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_user(
        self,
        conn: AsyncConnection,
        registered_user: dict[str, Any],
    ) -> None:
        # requires user to be registered
        user = await get_user(conn, registered_user["email"])
        assert_user(user)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_non_registered_user(
        self, conn: AsyncConnection, not_registered_email: str
    ) -> None:
        with pytest.raises(HTTPException):
            await get_user(conn, not_registered_email)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # requires user to be registered
        data = {
            "username": registered_user["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        token = response.json()
        assert_token(token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_invalid_password(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        invalid_password: str,
    ) -> None:
        # requires user to be registered
        data = {
            "username": registered_user["email"],
            "password": invalid_password,  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

        token = response.json()
        self.assert_invalid_token(token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_not_registered(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
        not_registered_email: str,
    ) -> None:
        # requires user to be registered
        data = {
            "username": not_registered_email,
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

        token = response.json()
        self.assert_invalid_token(token)
