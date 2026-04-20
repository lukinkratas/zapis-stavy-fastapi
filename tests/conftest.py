import uuid
from datetime import timedelta

import pytest

from api.routers.auth import create_access_token, create_confirmation_token


@pytest.fixture
def credentials() -> dict[str, str]:
    return {"email": "test@test.net", "password": "password"}


@pytest.fixture
def update_user_payload() -> dict[str, str]:
    return {"email": "update@test.net", "password": "update"}


@pytest.fixture
def location_payload() -> dict[str, str]:
    return {"name": "test"}


@pytest.fixture
def update_location_payload() -> dict[str, str]:
    return {"name": "test"}


@pytest.fixture
async def access_token(user_id: str) -> str:
    return create_access_token(user_id)


@pytest.fixture
async def confirmation_token(user_id: str) -> str:
    return create_confirmation_token(user_id)


@pytest.fixture
async def expired_access_token(user_id: str) -> str:
    return create_access_token(user_id, expires_delta=timedelta(-1))


@pytest.fixture
async def expired_confirmation_token(user_id: str) -> str:
    return create_confirmation_token(user_id, expires_delta=timedelta(-1))


@pytest.fixture
def not_registered_access_token() -> str:
    return create_access_token(str(uuid.uuid4()))
