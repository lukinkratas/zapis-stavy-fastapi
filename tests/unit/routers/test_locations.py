import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.locations import LocationsTable
from api.schemas.locations import LocationResponseJson


class TestUnitLocation:
    """Unit tests for locations."""

    @pytest.mark.anyio
    async def test_create_location(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = str(uuid.uuid4())
        location_from_db = location_payload | {
            "id": location_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user_id": str(uuid.uuid4()),
        }

        # mock
        mocker.patch.object(LocationsTable, "insert", return_value=location_from_db)

        # create location
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201

        new_location = response.json()
        assert LocationResponseJson.model_validate(new_location)

    @pytest.mark.anyio
    async def test_delete_location(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = str(uuid.uuid4())

        # mock
        mocker.patch.object(LocationsTable, "delete", return_value=None)

        # delete created location
        response = await async_client.delete(
            f"/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_update_location(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        update_location_payload: dict[str, str],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = str(uuid.uuid4())
        location_from_db = update_location_payload | {
            "id": location_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user_id": str(uuid.uuid4()),
        }

        # mock
        mocker.patch.object(LocationsTable, "update", return_value=location_from_db)

        # update location
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_location = response.json()
        assert LocationResponseJson.model_validate(updated_location)
