from typing import Any

import pytest
from httpx import AsyncClient

from tests.assertions import assert_meter


class TestIntegrationMeter:
    """Integration tests for meters."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_meter(
        self,
        async_client: AsyncClient,
        token: str,
    ) -> None:
        # create meter
        request_body = {"name": "test"}
        response = await async_client.post(
            "/meter",
            json=request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_meter = response.json()
        assert_meter(new_meter, **request_body)

        # delete created meter
        mid = new_meter["id"]
        response = await async_client.delete(f"/meter/{mid}")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_meter(
        self, async_client: AsyncClient, created_meter: dict[str, Any]
    ) -> None:
        mid = created_meter["id"]
        request_body = {"name": "update"}
        response = await async_client.put(f"/meter/{mid}", json=request_body)
        assert response.status_code == 200

        updated_meter = response.json()
        assert_meter(updated_meter, **request_body)

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_readings_on_meter(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        created_reading: dict[str, Any],
    ) -> None:
        mid = created_meter["id"]
        response = await async_client.get(f"/meter/{mid}/reading")
        assert response.status_code == 200
        readings = response.json()
        assert created_reading in readings

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_get_meter_with_readings(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        created_reading: dict[str, Any],
    ) -> None:
        meter_id = created_meter["id"]
        response = await async_client.get(f"/meter/{meter_id}")
        assert response.status_code == 200
        meter_with_readings = response.json()
        assert meter_with_readings == {
            "meter": created_meter,
            "readings": [created_reading],
        }
