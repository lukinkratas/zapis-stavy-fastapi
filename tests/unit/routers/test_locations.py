from typing import Any

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.locations import LocationsTable
from api.schemas import BaseResponse, ResponseWithId


class TestUnitLocation:
    """Unit tests for locations."""

    @pytest.mark.asyncio
    async def test_create_location(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        location_payload: dict[str, str],
        location_from_db: dict[str, Any],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        # mock
        mocker.patch.object(LocationsTable, "insert", return_value=location_from_db)

        # create location
        response = await test_client.post(
            "/v1/location",
            json=location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201
        assert ResponseWithId.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_delete_location(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        location_from_db: dict[str, Any],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = location_from_db["id"]

        # mock
        mocker.patch.object(LocationsTable, "delete", return_value=location_from_db)

        # delete created location
        response = await test_client.delete(
            f"/v1/location/{location_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_update_location(
        self,
        mocker: MockerFixture,
        test_client: AsyncClient,
        update_location_payload: dict[str, str],
        location_from_db: dict[str, Any],
        confirmed_user: dict[str, Any],
        access_token: str,
    ) -> None:
        location_id = location_from_db["id"]
        updated_location_from_db = location_from_db | update_location_payload

        # mock
        mocker.patch.object(
            LocationsTable, "update", return_value=updated_location_from_db
        )

        # update location
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_location_payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())
