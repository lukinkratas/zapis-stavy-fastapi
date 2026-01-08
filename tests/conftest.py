from typing import Any

import pytest

@pytest.fixture
def default_user() -> dict[str, Any]:
    return {
        "id": "e49a1d7f-50fc-4095-9740-346b79f4711b",
        "created_at": "2026-01-08T21:20:29.726628Z",
        "email": "default@email.net",
        "pssword": "xxx111"
    }

@pytest.fixture
def default_meter(default_user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "5ad4f210-cdfb-4196-82f7-af6afda013ea",
        "created_at": "2026-01-08T21:20:29.726628Z",
        "user_id": default_user["id"],
        "name": "default",
        "description": None,
    }


@pytest.fixture
def default_reading(default_meter: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "d09b982f-ffe7-42d1-809f-5c61eeac9f99",
        "created_at": "2026-01-08T21:20:29.748734Z",
        "meter_id": default_meter["id"],
        "value": 11.0,
    }
