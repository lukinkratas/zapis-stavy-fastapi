from unittest.mock import patch

import pytest
from httpx import AsyncClient

from api.repositories.locations import LocationRow, LocationsTable
from api.repositories.users import UserRow
from api.schemas import BaseResponse, Location, LocationsResponse, ResponseWithId


class TestUnitLocation:
    """Unit tests for locations."""

    @pytest.mark.asyncio
    async def test_create_location(
        self,
        test_client: AsyncClient,
        props: dict[str, str],
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        # mock
        with patch.object(LocationsTable, "insert", return_value=location_row):
            # create location
            response = await test_client.post(
                "/api/v1/locations",
                json=props,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert response.status_code == 201
        assert ResponseWithId.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_delete_location(
        self,
        test_client: AsyncClient,
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        location_id = location_row.id

        # mock
        with patch.object(LocationsTable, "delete", return_value=location_row):
            # delete created location
            response = await test_client.delete(
                f"/api/v1/locations/{location_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_update_location(
        self,
        test_client: AsyncClient,
        update_props: dict[str, str],
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        location_id = location_row.id
        updated_location_row = location_row._replace(**update_props)  # type: ignore [arg-type]

        # mock
        with patch.object(LocationsTable, "update", return_value=updated_location_row):
            # update location
            response = await test_client.put(
                f"/api/v1/locations/{location_id}",
                json=update_props,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_select_locations(
        self,
        test_client: AsyncClient,
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        # mock
        with patch.object(LocationsTable, "select", return_value=[location_row]):
            # select locations
            response = await test_client.get(
                "/api/v1/locations",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert LocationsResponse.model_validate(data)
        assert data["locations"] == [
            # serialize location into JSON (uuid and datetime becomes str)
            Location(**location_row._asdict()).model_dump(mode="json")
        ]
