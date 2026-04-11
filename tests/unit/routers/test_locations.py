from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.locations import LocationsTable
from tests.assertions import assert_location

from ..utils import location_factory


class TestUnitLocation:
    """Unit tests for locations."""

    @pytest.mark.anyio
    async def test_create_and_delete_location(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        registered_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_payload = {"name": "new"}

        # mocking
        new_location = location_factory(location_payload, registered_user["id"])
        mocker.patch.object(
            LocationsTable, "insert", new=AsyncMock(return_value=new_location)
        )

        # create location
        response = await async_client.post(
            "/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201

        new_location = response.json()
        assert_location(new_location)

        # delete created location
        mocker.patch.object(LocationsTable, "delete", new=AsyncMock(return_value=None))
        mid = new_location["id"]
        response = await async_client.delete(
            f"/location/{mid}", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 204

    @pytest.mark.anyio
    async def test_update_location(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        created_location: dict[str, Any],
        access_token: str,
    ) -> None:
        updated_location_payload = {"name": "update"}

        # mocking
        updated_location = created_location | updated_location_payload
        mocker.patch.object(
            LocationsTable, "update", new=AsyncMock(return_value=updated_location)
        )

        # update location
        mid = created_location["id"]
        response = await async_client.put(
            f"/location/{mid}",
            json=updated_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200

        updated_location = response.json()
        assert_location(updated_location)
