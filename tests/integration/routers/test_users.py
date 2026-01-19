from typing import Any

import pytest
from httpx import AsyncClient

from api.routers.auth import verify_password
from tests.assertions import assert_user


class TestIntegrationUser:
    """Integration tests for users."""

    @pytest.fixture
    def update_request_body(self) -> dict[str, str]:
        return {"email": "update@update.net", "password": "update5six7"}

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_and_delete_user(self, async_client: AsyncClient) -> None:
        # register user
        credentials = {"email": "integration@test.net", "password": "123456seven"}
        response = await async_client.post("/register", json=credentials)
        assert response.status_code == 201

        new_user = response.json()
        # pop password, cause it is hashed
        password = credentials.pop("password")
        assert verify_password(password, new_user["password"])
        assert_user(new_user, **credentials)

        # delete registered user
        uid = new_user["id"]
        response = await async_client.delete(f"/user/{uid}")
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_register_registered_user(
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
    async def test_delete_non_registered_user(
        self, async_client: AsyncClient, random_uuid: str
    ) -> None:
        response = await async_client.delete(f"/user/{random_uuid}")
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_user(
        self,
        async_client: AsyncClient,
        registered_user: dict[str, Any],
        update_request_body: dict[str, str],
    ) -> None:
        uid = registered_user["id"]
        response = await async_client.put(f"/user/{uid}", json=update_request_body)
        assert response.status_code == 200

        updated_user = response.json()
        assert_user(updated_user, **update_request_body)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_non_registered_user(
        self,
        async_client: AsyncClient,
        random_uuid: str,
        update_request_body: dict[str, str],
    ) -> None:
        response = await async_client.put(
            f"/user/{random_uuid}", json=update_request_body
        )
        assert response.status_code == 404
