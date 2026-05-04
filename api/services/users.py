import uuid
from psycopg import AsyncConnection
from ..models.users import users_table
from typing import Any
from ..auth import get_password_hash

async def register_user(conn: AsyncConnection, data: dict[str, Any]):
    plain_password = data.pop("password")
    data["password"] = get_password_hash(plain_password)
    await users_table.insert(conn, data)

async def delete_user(conn: AsyncConnection, user_id: str | uuid.UUID):
    await users_table.delete(conn, user_id)

async def update_user(conn: AsyncConnection, user_id: str | uuid.UUID, data: dict[str, Any]):

    if data.get("password") is not None:
        plain_password = data.pop("password")
        data["password"] = get_password_hash(plain_password)

    await users_table.update(conn, user_id, data)
