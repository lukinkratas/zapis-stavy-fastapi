import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from typing import Any

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.locations import LocationsTable
from api.schemas.locations import LocationResponseJson
from api.models.users import UsersTable


class TestUnitLocation:
    """Unit tests for locations."""

    @pytest.mark.anyio
    async def test_create_and_delete_location(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        confirmed_user: dict[str, Any],
        location_payload: dict[str, str],
        access_token: str,
    ) -> None:
        location_id = str(uuid.uuid4())
        location_from_db = location_payload | {
            "id": location_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user_id": str(uuid.uuid4()),
        }

        # mock
        mocker.patch.object(
            UsersTable,
            "select_by_id",
            new=AsyncMock(return_value=confirmed_user),
        )
        mocker.patch.object(
            LocationsTable, "insert", new=AsyncMock(return_value=location_from_db)
        )
        mocker.patch.object(LocationsTable, "delete", new=AsyncMock(return_value=None))

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
        confirmed_user: dict[str, Any],
        access_token: str,
        update_location_payload: dict[str, str],
    ) -> None:
        location_id = str(uuid.uuid4())
        location_from_db = update_location_payload | {
            "id": location_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "user_id": str(uuid.uuid4()),
        }

        # mock
        mocker.patch.object(
            UsersTable,
            "select_by_id",
            new=AsyncMock(return_value=confirmed_user),
        )
        mocker.patch.object(
            LocationsTable, "update", new=AsyncMock(return_value=location_from_db)
        )

        # update location
        response = await async_client.put(
            f"/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_location = response.json()
        assert LocationResponseJson.model_validate(updated_location)
