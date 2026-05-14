import uuid
from typing import Any

import pytest
from httpx import AsyncClient
from psycopg import AsyncConnection

from api.schemas import BaseResponse, ResponseWithId
from api.services.locations import (
    delete_location,
    select_location_by_id,
)


class TestCreate:
    """Integration tests for create location endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_location(
        self,
        test_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201
        assert ResponseWithId.model_validate(response.json())

        location_id = response.json()["id"]
        location_from_db = await select_location_by_id(db_conn, location_id)
        assert location_from_db is not None, "Location does not exist in db."

        # clean-up
        await delete_location(db_conn, location_id, confirmed_user["id"])

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_already_created_location(
        self,
        test_client: AsyncClient,
        created_location: dict[str, Any],
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 409

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_location_by_registered_user(
        self,
        test_client: AsyncClient,
        location_payload: dict[str, str],
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_location_with_expired_access_token(
        self,
        test_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        expired_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded exp."""
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_location_with_random_user_access_token(
        self,
        test_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        random_user_access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with random access token."""
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {random_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_location_with_confirmation_token(
        self,
        test_client: AsyncClient,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        confirmation_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing access token with different encoded typ."""
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401


class TestDelete:
    """Integration tests for delete location endpoints."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_location(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        created_location: dict[str, Any],
        access_token: str,
        db_conn: AsyncConnection,
    ) -> None:
        """Testing expected case."""
        location_id = created_location["id"]
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

        location_from_db = await select_location_by_id(db_conn, location_id)
        assert location_from_db is None, "Location still exists in db."

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_non_existing_location(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = uuid.uuid4()
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_location_with_expired_access_token(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        created_location: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        location_id = created_location["id"]
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_location_with_other_user_access_token(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        created_location: dict[str, Any],
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        location_id = created_location["id"]
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_location_with_random_user_access_token(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        created_location: dict[str, Any],
        random_user_access_token: str,
    ) -> None:
        """Testing access token with random access token."""
        location_id = created_location["id"]
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {random_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_location_with_confirmation_token(
        self,
        test_client: AsyncClient,
        confirmed_user: dict[str, Any],
        created_location: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with random access token."""
        location_id = created_location["id"]
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401


class TestUpdate:
    """Integration tests for update location endpoint."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_location(
        self,
        test_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        """Testing expected case."""
        location_id = created_location["id"]
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_non_existing_location(
        self,
        test_client: AsyncClient,
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = str(uuid.uuid4())
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404

    # async def test_update_location_by_registered_user() makes no sense
    # (In order to update a location, one has to be created first [by confirmed user])

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_location_with_expired_access_token(
        self,
        test_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        expired_access_token: str,
    ) -> None:
        """Testing access token with different encoded exp."""
        location_id = created_location["id"]
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_location_with_other_user_access_token(
        self,
        test_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        other_user_access_token: str,
    ) -> None:
        """Testing access token with different encoded sub."""
        location_id = created_location["id"]
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {other_user_access_token}"},
        )
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_location_with_random_user_access_token(
        self,
        test_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        random_user_access_token: str,
    ) -> None:
        """Testing access token with random access token."""
        location_id = created_location["id"]
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {random_user_access_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_location_with_confirmation_token(
        self,
        test_client: AsyncClient,
        created_location: dict[str, Any],
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        confirmation_token: str,
    ) -> None:
        """Testing access token with different encoded typ."""
        location_id = created_location["id"]
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {confirmation_token}"},
        )
        assert response.status_code == 401
