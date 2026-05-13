from typing import Any

import pytest
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.models.users import users_table
from api.schemas import Token


class TestLogin:
    """Integration tests for login endpoint."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_login_registered_user(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        """Testing expected case."""
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await test_client.post(
            "/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        token = response.json()
        assert Token.model_validate(token)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_login_confirmed_user(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        """Testing expected case."""
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await test_client.post(
            "/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200

        token = response.json()
        assert Token.model_validate(token)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_login_user_invalid_password(
        self,
        test_client: AsyncClient,
        creds: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        data = {
            "username": creds["email"],
            "password": "invalid",  # plain password
        }
        response = await test_client.post(
            "/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_login_not_registered_user(
        self,
        test_client: AsyncClient,
    ) -> None:
        data = {
            "username": "not@registered.net",
            "password": "password",  # plain password
        }
        response = await test_client.post(
            "/v1/auth/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401


class TestConfirm:
    """Integration tests for confirm endpoint."""

    @pytest.mark.asyncio
    async def test_confirm_user(
        self,
        test_client: AsyncClient,
        registered_user: dict[str, Any],
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        assert registered_user["confirmed"] is False, "User already confirmed."

        response = await test_client.get(f"/v1/auth/confirm/{confirmation_token}")

        assert response.status_code == 200
        user = await users_table.select_by_id(db_conn, registered_user["id"])
        assert user["confirmed"] is True, "User not confirmed."

    @pytest.mark.asyncio
    async def test_confirm_confirmed_user(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        response = await test_client.get(f"/v1/auth/confirm/{confirmation_token}")

        assert response.status_code == 200
        user = await users_table.select_by_id(db_conn, confirmed_user["id"])
        assert user["confirmed"] is True, "User not confirmed."


    @pytest.mark.asyncio
    async def test_confirm_user_with_expired_confirmation_token(
        self,
        test_client: AsyncClient,
        registered_user: dict[str, Any],
        expired_confirmation_token: str,
    ) -> None:
        """Testing confirmation token with different encoded exp."""
        response = await test_client.get(f"/v1/auth/confirm/{expired_confirmation_token}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_confirm_user_with_access_token(
        self,
        test_client: AsyncClient,
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await test_client.get(f"/v1/auth/confirm/{access_token}")
        assert response.status_code == 401