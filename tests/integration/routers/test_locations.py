from typing import Any

import pytest
from httpx import AsyncClient

from tests.assertions import assert_location


class TestIntegrationLocation:
    """Integration tests for locations."""

    @pytest.fixture
    def create_request_body(self) -> dict[str, str]:
        return {"name": "new"}

    @pytest.fixture
    def update_request_body(self) -> dict[str, str]:
        return {"name": "update"}

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_location(
        self,
        async_client: AsyncClient,
        token: str,
        create_request_body: dict[str, str],
    ) -> None:
        # create location
        response = await async_client.post(
            "/location",
            json=create_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_location = response.json()
        assert_location(new_location, **create_request_body)

        # delete created location
        mid = new_location["id"]
        response = await async_client.delete(
            f"/location/{mid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_existing_location(
        self,
        async_client: AsyncClient,
        token: str,
        created_location: dict[str, Any],
    ) -> None:
        # requires location to be already created
        create_request_body = {"name": created_location["name"]}
        response = await async_client.post(
            "/location",
            json=create_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 409

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_not_registered_email_token(
        self,
        async_client: AsyncClient,
        not_registered_email_token: str,
        create_request_body: dict[str, str],
    ) -> None:
        response = await async_client.post(
            "/location",
            json=create_request_body,
            headers={"Authorization": f"Bearer {not_registered_email_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_expired_token(
        self,
        async_client: AsyncClient,
        expired_access_token: str,
        create_request_body: dict[str, str],
    ) -> None:
        response = await async_client.post(
            "/location",
            json=create_request_body,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_non_existing_location(
        self,
        async_client: AsyncClient,
        random_uuid: str,
        token: str,
    ) -> None:
        response = await async_client.delete(
            f"/location/{random_uuid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_location(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        update_request_body: dict[str, str],
        token: str,
    ) -> None:
        mid = created_location["id"]
        response = await async_client.put(
            f"/location/{mid}",
            json=update_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        updated_location = response.json()
        assert_location(updated_location, **update_request_body)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_non_existing_location(
        self,
        async_client: AsyncClient,
        random_uuid: str,
        update_request_body: dict[str, str],
        token: str,
    ) -> None:
        response = await async_client.put(
            f"/location/{random_uuid}",
            json=update_request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
