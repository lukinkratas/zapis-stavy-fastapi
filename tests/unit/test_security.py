import pytest

from api.repositories.users import UserRow
from api.security import verify_password


@pytest.mark.asyncio
async def test_verify_password(creds: dict[str, str], registered_user: UserRow) -> None:
    verify_password(creds["password"], registered_user.password_hash)
