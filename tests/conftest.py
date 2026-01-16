# @pytest.fixture
# def default_credentials() -> dict[str, str]:
#     return {"email": "default@email.net", "password": "xxx111"}
#
#
# @pytest.fixture
# def default_user(default_credentials: dict[str, str]) -> dict[str, str]:
#     return default_credentials | {
#         "id": "e49a1d7f-50fc-4095-9740-346b79f4711b",
#         "created_at": "2026-01-08T21:20:29.726628Z",
#     }
#
#
# @pytest.fixture
# def default_user_from_db(default_user: dict[str, str]) -> dict[str, str]:
#     default_user_from_db = default_user.copy()
#     plain_password = default_user_from_db.pop("password")
#     default_user_from_db["password"] = get_password_hash(plain_password)
#     return default_user_from_db
#
#
# @pytest.fixture
# def default_meter(default_user: dict[str, Any]) -> dict[str, Any]:
#     return {
#         "id": "5ad4f210-cdfb-4196-82f7-af6afda013ea",
#         "created_at": "2026-01-12T14:28:54.840054Z",
#         "user_id": default_user["id"],
#         "name": "default",
#     }
#
#
# @pytest.fixture
# def default_reading(
#     default_meter: dict[str, Any], default_user: dict[str, Any]
# ) -> dict[str, Any]:
#     return {
#         "id": "d09b982f-ffe7-42d1-809f-5c61eeac9f99",
#         "created_at": "2026-01-12T14:28:54.857578Z",
#         "meter_id": default_meter["id"],
#         "user_id": default_user["id"],
#         "value": 11.0,
#     }
#
#
# @pytest.fixture
# def default_token(default_user: dict[str, Any]) -> str:
#     return create_access_token(default_user["email"])
