from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from api.models.readings import ReadingsTable
from tests.assertions import assert_reading

from ..utils import reading_factory


class TestUnitReading:
    """Unit tests for readings."""

    @pytest.mark.anyio
    async def test_create_and_delete_reading(
        self,
        mocker: MockerFixture,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        registered_user: dict[str, Any],
        token: str,
    ) -> None:
        reading_payload = {"value": 99.0, "meter_id": created_meter["id"]}

        # mocking
        new_reading = reading_factory(reading_payload, registered_user["id"])
        mocker.patch.object(
            ReadingsTable, "insert", new=AsyncMock(return_value=new_reading)
        )

        # create reading
        response = await async_client.post(
            "/reading",
            json=reading_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_reading = response.json()
        assert_reading(new_reading)

        # delete created reading
        mocker.patch.object(ReadingsTable, "delete", new=AsyncMock(return_value=None))
        rid = new_reading["id"]
        response = await async_client.delete(
            f"/reading/{rid}", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

    @pytest.mark.anyio
    async def test_update_reading(
        self,
        async_client: AsyncClient,
        mocker: MockerFixture,
        created_reading: dict[str, Any],
        token: str,
    ) -> None:
        updated_reading_payload = {"value": 55.0}

        # mocking
        updated_reading = created_reading | updated_reading_payload
        mocker.patch.object(
            ReadingsTable, "update", new=AsyncMock(return_value=updated_reading)
        )

        # update reading
        rid = created_reading["id"]
        response = await async_client.put(
            f"/reading/{rid}",
            json=updated_reading_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        updated_reading = response.json()
        assert_reading(updated_reading)
