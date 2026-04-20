import pytest

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