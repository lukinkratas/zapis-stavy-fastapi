from typing import Any

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.models.users import users_table
from api.routers.auth import (
    authenticate_user,
    get_current_confirmed_user,
    get_current_user,
)
from api.schemas.auth import Token
from api.schemas.users import UserResponseJson


class TestLogin:
    """Integration tests for login endpoint."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_registered_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        """Testing expected case."""
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
    async def test_login_confirmed_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        """Testing expected case."""
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
    async def test_login_user_invalid_password(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
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
    async def test_login_not_registered_user(
        self,
        async_client: AsyncClient,
    ) -> None:
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


class TestConfirm:
    """Integration tests for confirm endpoint."""

    @pytest.mark.anyio
    async def test_confirm_registered_user(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        assert registered_user["confirmed"] is False
        response = await async_client.get(f"/confirm/{confirmation_token}")
        assert response.status_code == 200
        user = await users_table.select_by_id(db_conn, registered_user["id"])
        assert user["confirmed"] is True

    @pytest.mark.anyio
    async def test_confirm_confirmed_user(
        self,
        async_client: AsyncClient,
        confirmed_user: dict[str, Any],
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        response = await async_client.get(f"/confirm/{confirmation_token}")
        assert response.status_code == 200
        user = await users_table.select_by_id(db_conn, confirmed_user["id"])
        assert user["confirmed"] is True

    @pytest.mark.anyio
    async def test_confirm_user_with_other_user_access_token(
        self, async_client: AsyncClient, other_user_access_token: str
    ) -> None:
        """Testing access token with different encoded sub."""
        response = await async_client.get(f"/confirm/{other_user_access_token}")
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_confirm_user_with_expired_access_token(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        expired_confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await async_client.get(f"/confirm/{expired_confirmation_token}")
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_confirm_user_with_access_token(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.get(f"/confirm/{access_token}")
        assert response.status_code == 401


class TestOther:
    """Integration tests for other auth helper and private functions."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user(
        self,
        db_conn: AsyncConnection,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        """Testing expected case."""
        user = await authenticate_user(db_conn, **credentials)
        assert UserResponseJson.model_validate(user)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user_not_registered_email(
        self, db_conn: AsyncConnection
    ) -> None:
        with pytest.raises(HTTPException):
            await authenticate_user(db_conn, "not@registered.net", "password")

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user_invalid_password(
        self,
        db_conn: AsyncConnection,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        with pytest.raises(HTTPException):
            await authenticate_user(db_conn, credentials["email"], "invalid")

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user(
        self,
        db_conn: AsyncConnection,
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing expected case."""
        user = await get_current_user(db_conn, access_token)
        assert UserResponseJson.model_validate(user)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_with_other_user_access_token(
        self, db_conn: AsyncConnection, other_user_access_token: str
    ) -> None:
        """Testing access token with different encoded sub."""
        with pytest.raises(HTTPException):
            await get_current_user(db_conn, other_user_access_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_with_expired_access_token(
        self,
        db_conn: AsyncConnection,
        registered_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        with pytest.raises(HTTPException):
            await get_current_user(db_conn, expired_access_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_with_confirmation_token(
        self,
        db_conn: AsyncConnection,
        registered_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        with pytest.raises(HTTPException):
            await get_current_user(db_conn, confirmation_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_confirmed_user(
        self, confirmed_user: dict[str, Any]
    ) -> None:
        """Testing expected case."""
        assert await get_current_confirmed_user(confirmed_user) == confirmed_user

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_confirmed_user_not_confirmed(
        self, registered_user: dict[str, Any]
    ) -> None:
        with pytest.raises(HTTPException):
            await get_current_confirmed_user(registered_user)
