from typing import Any

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.models.users import users_table
from api.routers.auth import (
    authenticate_user,
    credentials_exception,
    get_current_user,
)
from api.schemas.auth import Token
from api.schemas.users import UserResponseJson


class TestIntegrationAuth:
    """Integration tests for auth."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user(
        self,
        conn: AsyncConnection,
        credentials: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        # requires user to be already registered
        user = await authenticate_user(conn, **credentials)
        assert UserResponseJson.model_validate(user)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user_not_confirmed(
        self,
        conn: AsyncConnection,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # requires user to be already registered
        with pytest.raises(HTTPException):
            await authenticate_user(conn, **credentials)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user_not_registered_email(
        self, conn: AsyncConnection
    ) -> None:
        # requires user to be already registered
        with pytest.raises(HTTPException):
            await authenticate_user(conn, "not@registered.net", "password")

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user_invalid_password(
        self,
        conn: AsyncConnection,
        credentials: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        # requires user to be already registered
        with pytest.raises(HTTPException):
            await authenticate_user(conn, credentials["email"], "invalid")

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user(
        self, conn: AsyncConnection, access_token: str
    ) -> None:
        # requires user to be registered
        user = await get_current_user(conn, access_token)
        assert UserResponseJson.model_validate(user)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_not_registered_access_token(
        self, conn: AsyncConnection, not_registered_access_token: str
    ) -> None:
        # requires user to be registered
        with pytest.raises(HTTPException):
            await get_current_user(conn, not_registered_access_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_expired_token(
        self, conn: AsyncConnection, expired_access_token: str
    ) -> None:
        # requires user to be registered
        with pytest.raises(HTTPException):
            await get_current_user(conn, expired_access_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_confirmation_token(
        self, conn: AsyncConnection, confirmation_token: str
    ) -> None:
        # requires user to be registered
        with pytest.raises(HTTPException):
            await get_current_user(conn, confirmation_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        # requires user to be registered
        data = {
            "username": credentials["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        token = response.json()
        assert Token.model_validate(token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_invalid_password(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        # requires user to be registered
        data = {
            "username": credentials["email"],
            "password": "invalid",  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_not_registered(
        self,
        async_client: AsyncClient,
    ) -> None:
        # requires user to be registered
        data = {
            "username": "not@registered.net",
            "password": "password",  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_not_confirmed(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # requires user to be registered
        data = {
            "username": credentials["email"],
            "password": credentials["password"],  # plain password
        }
        response = await async_client.post(
            "/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_confirm(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        confirmation_token: str,
        conn: AsyncConnection,
    ) -> None:
        # confirm
        assert registered_user["confirmed"] is False
        response = await async_client.get(f"/confirm/{confirmation_token}")
        assert response.status_code == 200
        user = await users_table.select_by_id(conn, registered_user["id"])
        assert user["confirmed"] is True

    @pytest.mark.anyio
    async def test_confirm_expired_token(
        self, async_client: AsyncClient, expired_confirmation_token: str
    ) -> None:
        response = await async_client.get(f"/confirm/{expired_confirmation_token}")
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_confirm_access_token(
        self, async_client: AsyncClient, access_token: str
    ) -> None:
        response = await async_client.get(f"/confirm/{access_token}")
        assert response.status_code == 401
