from typing import Any

import pytest
from httpx import AsyncClient

from tests.assertions import assert_reading


class TestIntegrationReading:
    """Integration tests for readings."""

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_create_and_delete_reading(
        self,
        async_client: AsyncClient,
        created_meter: dict[str, Any],
        token: str,
    ) -> None:
        # create reading
        request_body = {"meter_id": created_meter["id"], "value": 99.0}
        response = await async_client.post(
            "/reading",
            json=request_body,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

        new_reading = response.json()
        assert_reading(new_reading, **request_body)

        # delete created reading
        rid = new_reading["id"]
        response = await async_client.delete(f"/reading/{rid}")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.anyio
    async def test_update_reading(
        self, async_client: AsyncClient, created_reading: dict[str, Any]
    ) -> None:
        rid = created_reading["id"]
        request_body = {"value": 55.0}
        response = await async_client.put(f"/reading/{rid}", json=request_body)
        assert response.status_code == 200

        updated_reading = response.json()
        assert_reading(updated_reading, **request_body)
