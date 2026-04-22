from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from api.routers.auth import create_access_token, verify_password
from api.schemas.users import UserResponseJson


class TestCreateAndDelete:
    """Integration tests for create and delete user endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        mock_send_email: MagicMock,
    ) -> None:
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

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_already_registered_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        registered_user: dict[str, Any],
    ) -> None:
        # requires user to be already registered
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 409

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_user_random_id_access_token(
        self, async_client: AsyncClient, random_id_access_token: str
    ) -> None:
        response = await async_client.delete(
            "/user", headers={"Authorization": f"Bearer {random_id_access_token}"}
        )
        assert response.status_code == 401


class TestUpdate:
    """Integration tests for update user endpoint."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        update_user_payload: dict[str, str],
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
        assert updated_user["email"] == update_user_payload["email"]
        # TODO: fetch the password from db (not to be displayed in UserResponseJson)
        # assert verify_password(update_user_payload["password"], updated_user.password)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user_random_id_access_token(
        self,
        async_client: AsyncClient,
        update_user_payload: dict[str, str],
        random_id_access_token: str,
    ) -> None:
        response = await async_client.put(
            "/user",
            json=update_user_payload,
            headers={"Authorization": f"Bearer {random_id_access_token}"},
        )
        assert response.status_code == 401
