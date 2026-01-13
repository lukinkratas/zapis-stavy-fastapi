from typing import Any

import pytest

from api.routers.auth import get_password_hash


@pytest.fixture
def default_user() -> dict[str, Any]:
    return {
        "id": "e49a1d7f-50fc-4095-9740-346b79f4711b",
        "created_at": "2026-01-08T21:20:29.726628Z",
        "email": "default@email.net",
        "password": "xxx111",
    }


@pytest.fixture
def hashed_password(default_user: dict[str, Any]) -> str:
    return get_password_hash(default_user["password"])


@pytest.fixture
def default_meter(default_user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "5ad4f210-cdfb-4196-82f7-af6afda013ea",
        "created_at": "2026-01-12T14:28:54.840054Z",
        "user_id": default_user["id"],
        "name": "default",
    }


@pytest.fixture
def default_reading(default_meter: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": "d09b982f-ffe7-42d1-809f-5c61eeac9f99",
        "created_at": "2026-01-12T14:28:54.857578Z",
        "meter_id": default_meter["id"],
        "value": 11.0,
    }
