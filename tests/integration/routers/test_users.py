from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.models.users import users_table
from api.routers.auth import create_access_token


class TestRegisterAndDelete:
    """Integration tests for create and delete user endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self,
        async_client: AsyncClient,
        creds: dict[str, str],
        mock_send_email: MagicMock,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        # register user
        response = await async_client.post("/v1/register", json=creds)
        assert response.status_code == 201
        mock_send_email.assert_called_once()

        user_from_db = await users_table.select_by_email(db_conn, creds["email"])
        assert user_from_db is not None, "User does not exist in db."

        # delete registered user
        user_id = response.json()["id"]
        access_token = create_access_token(user_id)
        response = await async_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        user_from_db = await users_table.select_by_email(db_conn, creds["email"])
        assert user_from_db is None, "User still exists in db."


class TestRegister:
    """Integration tests for create user endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_already_registered_user(
        self,
        async_client: AsyncClient,
        creds: dict[str, str],
        registered_user_id: str,
    ) -> None:
        response = await async_client.post("/v1/register", json=creds)
        assert response.status_code == 409

    @pytest.mark.parametrize(
        "creds",
        [
            pytest.param({"email": "test@test.net"}, id="missing password"),
            pytest.param({"password": "password"}, id="missing email"),
            pytest.param(
                {"username": "test@test.net", "password": "password"},
                id="username instead of email",
            ),
        ],
    )
    @pytest.mark.anyio
    async def test_register_invalid_schema(
        self, async_client: AsyncClient, creds: dict[str, str]
    ) -> None:
        # register user
        response = await async_client.post("/v1/register", json=creds)
        assert response.status_code == 422


class TestDelete:
    """Integration tests for delete user endpoints."""

    # async def test_delete_confirmed_user() errors the user fixture teardown

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_user_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        registered_user_id: str,
        other_confirmed_user_id: str,
        other_user_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded sub."""
        registered_user_from_db = await users_table.select_by_id(db_conn, registered_user_id)
        assert registered_user_from_db is not None, "User does not exist in db."

        other_confirmed_user_from_db = await users_table.select_by_id(
            db_conn, other_confirmed_user_id
        )
        assert other_confirmed_user_from_db is not None, (
            "Other user does not exist in db."
        )

        response = await async_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {other_user_access_token}"}
        )
        assert response.status_code == 200

        registered_user_from_db = await users_table.select_by_id(
            db_conn, registered_user_id
        )
        assert registered_user_from_db is not None, "User was deleted by other user."

        other_confirmed_user_from_db = await users_table.select_by_id(
            db_conn, other_confirmed_user_id
        )
        assert other_confirmed_user_from_db is None, "Other user was not deleted"

    @pytest.mark.integration
    @pytest.mark.anyio
    # async def test_delete_non_existing_user(
    async def test_delete_user_with_not_registered_user_access_token(
        self,
        async_client: AsyncClient,
        registered_user_id: str,
        not_registered_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub, that is not registered."""
        response = await async_client.delete(
            "/v1/user",
            headers={"Authorization": f"Bearer {not_registered_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_user_with_expired_access_token(
        self,
        async_client: AsyncClient,
        registered_user_id: str,
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await async_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {expired_access_token}"}
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_user_with_confirmation_token(
        self,
        async_client: AsyncClient,
        registered_user_id: str,
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.delete(
            "/v1/user", headers={"Authorization": f"Bearer {confirmation_token}"}
        )
        assert response.status_code == 401


class TestUpdate:
    """Integration tests for update user endpoint."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user_id: str,
        access_token: str,
    ) -> None:
        """Testing expected case."""
        response = await async_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_confirmed_user(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        confirmed_user_id: str,
        access_token: str,
    ) -> None:
        response = await async_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user_id: str,
        other_user_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded sub."""
        user_pre = await users_table.select_by_id(db_conn, registered_user_id)
        response = await async_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 200
        user_post = await users_table.select_by_id(db_conn, registered_user_id)
        assert user_pre == user_post, "User was update by other user."

    @pytest.mark.integration
    @pytest.mark.anyio
    # async def test_update_non_existing_user(
    async def test_update_user_with_not_registered_user_access_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user_id: str,
        not_registered_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub, that is not registered."""
        response = await async_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {not_registered_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user_with_expired_access_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user_id: str,
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await async_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user_with_confirmation_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user_id: str,
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.put(
            "/v1/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401
