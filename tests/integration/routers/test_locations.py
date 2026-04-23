import uuid
from typing import Any

import pytest
from httpx import AsyncClient

from api.schemas.locations import LocationResponseJson


class TestCreateAndDelete:
    """Integration tests for create and delete location endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_location(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing expected case."""
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


class TestCreate:
    """Integration tests for create location endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_already_created_location(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 409


    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_by_registered_user(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_with_expired_access_token(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_location_with_confirmation_token(
        self,
        async_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401


class TestDelete:
    """Integration tests for delete location endpoints."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_non_existing_location(
        self,
        async_client: AsyncClient,
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = uuid.uuid4()
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200


    # async def test_delete_location_by_registered_user() makes no sense
    # (In order to delete a location, one has to be created first [by confirmed user])

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_location_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        location_id = created_location["id"]
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_location_with_expired_access_token(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        confirmed_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        location_id = created_location["id"]
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_delete_location_with_confirmation_token(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        confirmed_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        location_id = created_location["id"]
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401


class TestUpdate:
    """Integration tests for update location endpoint."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_location(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing expected case."""
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
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = str(uuid.uuid4())
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404


    # async def test_update_location_by_registered_user() makes no sense
    # (In order to update a location, one has to be created first [by confirmed user])

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_location_with_other_user_access_token(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        location_id = created_location["id"]
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_location_with_expired_access_token(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        location_id = created_location["id"]
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_location_with_confirmation_token(
        self,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        location_id = created_location["id"]
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401
