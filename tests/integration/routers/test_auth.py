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


class TestLogin:
    """Integration tests for login endpoint."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_login_registered_user(
        self,
        async_client: AsyncClient,
        creds: dict[str, str],
        registered_user_id: str,
    ) -> None:
        """Testing expected case."""
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await async_client.post(
            "/v1/token",
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
        creds: dict[str, str],
        confirmed_user_id: str,
    ) -> None:
        """Testing expected case."""
        data = {
            "username": creds["email"],
            "password": creds["password"],  # plain password
        }
        response = await async_client.post(
            "/v1/token",
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
        creds: dict[str, str],
        registered_user_id: str,
    ) -> None:
        data = {
            "username": creds["email"],
            "password": "invalid",  # plain password
        }
        response = await async_client.post(
            "/v1/token",
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
            "/v1/token",
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
        registered_user_id: str,
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        registered_user = await users_table.select_by_id(db_conn, registered_user_id)
        assert registered_user["confirmed"] is False, "User already confirmed."

        response = await async_client.get(f"/v1/confirm/{confirmation_token}")

        assert response.status_code == 200
        user = await users_table.select_by_id(db_conn, registered_user_id)
        assert user["confirmed"] is True, "User not confirmed."

    @pytest.mark.anyio
    async def test_confirm_confirmed_user(
        self,
        async_client: AsyncClient,
        confirmed_user_id: str,
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        response = await async_client.get(f"/v1/confirm/{confirmation_token}")

        assert response.status_code == 200
        user = await users_table.select_by_id(db_conn, confirmed_user_id)
        assert user["confirmed"] is True, "User not confirmed."

    # async def test_confirm_user_with_other_user_confirmation_token( makes no sense
    # it is seting the same case as is already tested on test_confirm_registered_user

    @pytest.mark.anyio
    async def test_confirm_user_with_not_registered_user_confirmation_token(
        self, async_client: AsyncClient, not_registered_user_confirmation_token: str
    ) -> None:
        """Testing confirmation token with different encoded sub, not registered."""
        response = await async_client.get(
            f"/v1/confirm/{not_registered_user_confirmation_token}"
        )
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_confirm_user_with_expired_confirmation_token(
        self,
        async_client: AsyncClient,
        registered_user_id: str,
        expired_confirmation_token: str,
    ) -> None:
        """Testing confirmation token with different encoded exp."""
        response = await async_client.get(f"/v1/confirm/{expired_confirmation_token}")
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_confirm_user_with_access_token(
        self,
        async_client: AsyncClient,
        registered_user_id: str,
        access_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.get(f"/v1/confirm/{access_token}")
        assert response.status_code == 401


class TestOther:
    """Integration tests for other auth helper and private functions."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_authenticate_user(
        self,
        db_conn: AsyncConnection,
        creds: dict[str, str],
        registered_user_id: str,
    ) -> None:
        """Testing expected case."""
        await authenticate_user(db_conn, **creds)

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
        creds: dict[str, str],
        registered_user_id: str,
    ) -> None:
        with pytest.raises(HTTPException):
            await authenticate_user(db_conn, creds["email"], "invalid")

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user(
        self,
        db_conn: AsyncConnection,
        registered_user_id: str,
        access_token: str,
    ) -> None:
        """Testing expected case."""
        await get_current_user(db_conn, access_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_with_not_registered_user_access_token(
        self, db_conn: AsyncConnection, not_registered_user_access_token: str
    ) -> None:
        """Testing access token with different encoded sub, that is not registered."""
        with pytest.raises(HTTPException):
            await get_current_user(db_conn, not_registered_user_access_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_user_with_expired_access_token(
        self,
        db_conn: AsyncConnection,
        registered_user_id: str,
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
        registered_user_id: str,
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        with pytest.raises(HTTPException):
            await get_current_user(db_conn, confirmation_token)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_confirmed_user(
        self, db_conn: AsyncConnection, confirmed_user_id: str,
    ) -> None:
        """Testing expected case."""
        confirmed_user = await users_table.select_by_id(db_conn, confirmed_user_id)
        assert await get_current_confirmed_user(confirmed_user)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_current_confirmed_user_not_confirmed(
        self, db_conn: AsyncConnection, registered_user_id: str
    ) -> None:
        registered_user = await users_table.select_by_id(db_conn, registered_user_id)
        with pytest.raises(HTTPException):
            await get_current_confirmed_user(registered_user)
