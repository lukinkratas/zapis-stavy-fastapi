import uuid
from typing import Any

import pytest
from httpx import AsyncClient

from api.schemas.locations import LocationResponseJson


class TestIntegrationLocation:
    """Integration tests for locations."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_location(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        access_token: str,
        confirmed_user: dict[str, Any],
    ) -> None:
        # create location
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201

        new_location = response.json()
        assert LocationResponseJson.model_validate(new_location)

        # delete created location
        location_id = new_location["id"]
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_existing_location(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        created_location: dict[str, Any],
        access_token: str,
        confirmed_user: dict[str, Any],
    ) -> None:
        # requires location to be already created
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 409

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_random_id_access_token(
        self,
        async_client: AsyncClient,
        random_id_access_token: str,
        location_payload: dict[str, str],
    ) -> None:
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {random_id_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_expired_token(
        self,
        async_client: AsyncClient,
        expired_access_token: str,
        location_payload: dict[str, str],
    ) -> None:
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_non_existing_location(
        self,
        async_client: AsyncClient,
        access_token: str,
        confirmed_user: dict[str, Any],
    ) -> None:
        response = await async_client.delete(
            f"/location/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_location(
        self,
        async_client: AsyncClient,
        access_token: str,
        update_location_payload: dict[str, str],
        created_location: dict[str, Any],
        confirmed_user: dict[str, Any],
    ) -> None:
        location_id = created_location["id"]
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_location = response.json()
        assert LocationResponseJson.model_validate(updated_location)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_non_existing_location(
        self,
        async_client: AsyncClient,
        access_token: str,
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
    ) -> None:
        location_id = str(uuid.uuid4())
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404
