from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from api.routers.auth import create_access_token, verify_password
from api.schemas.users import UserResponseJson


class TestRegisterAndDelete:
    """Integration tests for create and delete user endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        mock_send_email: MagicMock,
    ) -> None:
        """Testing expected case."""
        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201
        mock_send_email.assert_called_once()

        registered_user = response.json()["user"]
        assert UserResponseJson.model_validate(registered_user)
        assert registered_user["email"] == credentials["email"]
        assert verify_password(credentials["password"], registered_user["password"])

        # delete registered user
        access_token = create_access_token(registered_user["id"])
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200


class TestRegister:
    """Integration tests for create user endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_already_registered_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 409

    @pytest.mark.parametrize(
        "credentials",
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
        self, async_client: AsyncClient, credentials: dict[str, str]
    ) -> None:
        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 422


class TestDelete:
    """Integration tests for delete user endpoints."""

    # async def test_delete_confirmed_user() errors the user fixture teardown

    @pytest.mark.integration
    @pytest.mark.anyio
    # async def test_delete_non_existing_user(
    async def test_delete_user_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {other_user_access_token}"}
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_user_with_expired_access_token(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {expired_access_token}"}
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_user_with_confirmation_token(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {confirmation_token}"}
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
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing expected case."""
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_user = response.json()
        assert UserResponseJson.model_validate(updated_user)
        # TODO: fetch the password from db (not to be displayed in UserResponseJson)
        # assert verify_password(update_user_payload["password"], updated_user.password)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_confirmed_user(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_user = response.json()
        assert UserResponseJson.model_validate(updated_user)

    @pytest.mark.integration
    @pytest.mark.anyio
    # async def test_update_non_existing_user(
    async def test_update_user_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user_with_expired_access_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        registered_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await async_client.put(
            "/user",
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
        registered_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401
