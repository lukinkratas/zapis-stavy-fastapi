import uuid
from typing import Any

import pytest
from httpx import AsyncClient

from api.routers.auth import verify_password
from api.schemas.users import UserResponseJson


class TestIntegrationUser:
    """Integration tests for users."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(
        self, async_client: AsyncClient, credentials: dict[str, str]
    ) -> None:
        # register user
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201

        registered_user = response.json()["user"]
        assert UserResponseJson.model_validate(registered_user)
        assert registered_user["email"] == credentials["email"]
        assert verify_password(credentials["password"], registered_user["password"])

        # delete registered user
        uid = registered_user["id"]
        response = await async_client.delete(f"/user/{uid}")
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_registered_user(
        self,
        async_client: AsyncClient,
        credentials: dict[str, str],
        user_from_db: dict[str, Any],
    ) -> None:
        # requires user to be already registered
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 409

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_non_registered_user(self, async_client: AsyncClient) -> None:
        response = await async_client.delete(f"/user/{uuid.uuid4()}")
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user(
        self,
        async_client: AsyncClient,
        user_id: str,
    ) -> None:
        update_body = {"email": "update@test.net", "password": "update"}
        response = await async_client.put(f"/user/{user_id}", json=update_body)
        assert response.status_code == 200

        updated_user = response.json()
        assert UserResponseJson.model_validate(updated_user)
        assert updated_user["email"] == update_body["email"]
        # TODO: fetch the password from db (not to be displayed in UserResponseJson)
        # assert verify_password(update_body["password"], updated_user.password)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_non_registered_user(self, async_client: AsyncClient) -> None:
        update_body = {"email": "update@test.net", "password": "update"}
        response = await async_client.put(f"/user/{uuid.uuid4()}", json=update_body)
        assert response.status_code == 404
