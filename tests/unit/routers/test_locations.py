import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.repositories.locations import LocationRow, LocationsTable
from api.repositories.users import UserRow
from api.schemas import BaseResponse, ResponseWithId


class TestUnitLocation:
    """Unit tests for locations."""

    @pytest.mark.asyncio
    async def test_create_location(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        props: dict[str, str],
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        # mock
        mocker.patch.object(LocationsTable, "insert", return_value=location_row)

        # create location
        response = await test_client.post(
            "/v1/location",
            json=props,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 201
        assert ResponseWithId.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_delete_location(
        self,
        test_client: AsyncClient,
        mocker: MockerFixture,
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        location_id = location_row.id

        # mock
        mocker.patch.object(LocationsTable, "delete", return_value=location_row)

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
        update_props: dict[str, str],
        location_row: LocationRow,
        confirmed_user: UserRow,
        access_token: str,
    ) -> None:
        location_id = location_row.id
        updated_location_row = location_row._replace(**update_props)

        # mock
        mocker.patch.object(LocationsTable, "update", return_value=updated_location_row)

        # update location
        response = await test_client.put(
            f"/v1/location/{location_id}",
            json=update_props,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert BaseResponse.model_validate(response.json())
