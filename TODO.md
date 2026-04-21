- [x] add e2e testing
- [x] review e2e postman collection
- [x] user endpoints with access token
- [x] login and register - same form -> Nope
- [x] DEL/PUT endpoints - user_id from JWT token, not in endpoint name
- [ ] confirmed only in authorize, or in get_current_user as is in fast api docs? -> get_current_user + get_current_confirmed_user -> allow to login and resend confirmation token
- [ ] refactor tests
- [ ] tests for deleteing, updating different user data
- [ ] tests update - every token dependent endpoint test with valid, expired, random_id_token
- [ ] tests update - every user dependent endpoint test with confirmed and not confirmed user
- [ ] review coverage
- [ ] Dockerfile
- [ ] AWS logs service like logtail
- [ ] api version in the name
- [ ] detail -> message
- [ ] register endpoint user field returns password bug
- [ ] remove confirmation url from register response json
- [ ] sqlalchemy orm?
- [ ] upload pic + ORM
- [ ] LLM advisory + langfuse observability
- [ ] review unit tests and review all test cases coverage
- [ ] review int tests and review all test cases coverage
- [x] switch from meters to locations
- [x] use confirmation token
- [x] testcontainers for integration tests
- [x] id as sub for access token and confirmation token -> confirmation token update table without get_user middle step, be careful with get_uset + authenticate user (comes with email from web form)

  1.2 DELETE endpoints return 204 even when resource doesn't exist (api/routers/users.py, api/routers/meters.py)
  DELETE /user/{id} and DELETE /meter/{id} return 204 regardless of whether the row existed. This silently swallows
  client errors (wrong ID, double-delete). Consider returning 404 when rowcount == 0.

  1.4 Password returned in user responses (api/schemas/users.py)
  UserResponseJson includes the password (hashed) field. Even hashed, exposing password hashes to API consumers is a
   security anti-pattern. Remove it from the response schema.

  Significant Issues

  1.5 Rate limit of 1 req/min is unusable (api/main.py)
  default_limits=["1/minute"] will break any real client interaction. This seems like a dev leftover — should be
  configurable per environment.

  1.6 create_confirmation_token is unused
  It's defined in api/auth.py but never called anywhere — dead code.

  ---
  2. Code Quality

  2.1 Raw SQL with string interpolation risk (api/models/base.py)
  The table_name is inserted via sql.Identifier, which is correct. However, build_set_clause in api/utils.py uses
  sql.Identifier for column names from user-supplied dict keys. While psycopg's sql.Identifier escapes properly, the
   pattern of building SQL from request body keys is fragile — a schema change or unexpected field could produce
  confusing SQL errors. Consider validating columns against an allowlist.

  2.2 BaseTable stores conn as instance state (api/models/base.py)
  Each request creates model instances with a connection reference. This works but couples model lifetime to
  connection lifetime. If a model instance is accidentally retained past the request, it holds a stale connection.

  2.3 Logging decorators add noise (api/utils.py)
  log_func and log_async_func log every call at INFO level with full args. In production with auth flows, this could
   log sensitive data (passwords, tokens). At minimum, redact sensitive parameters.

  2.4 No __all__ exports — minor, but with from module import * patterns this could leak internals.

  ---
  3. Security

  3.1 CRITICAL: Unprotected user mutation endpoints (repeated from 1.3)
  This is the highest-severity finding. PUT /user/{id} and DELETE /user/{id} are completely open.

  3.2 SECRET_KEY in .env is committed (.env is in the repo)
  Check .gitignore — if .env is tracked, the secret key is exposed. Even for dev, this sets a bad precedent. The
  .env.example file exists; .env should be gitignored.

  3.3 No input validation on email format (api/schemas/users.py)
  UserCreateRequestBody.email is just str. Use Pydantic's EmailStr for basic validation.

  3.4 JWT has no audience/issuer claims (api/auth.py)
  Tokens only contain sub, type, and exp. Missing iss/aud makes token reuse across services easier if the same
  SECRET_KEY leaks.

  3.5 No password strength validation
  UserCreateRequestBody.password accepts any string, including empty.

  ---
  4. Performance

  4.1 No index on meters.user_id (sql/meters.sql)
  DELETE /meter/{id} and select_by_id filter by both id and user_id. There's a PK index on id but no index on
  user_id, which will matter as the table grows.

  4.2 Connection pool sizing not configurable
  AsyncConnectionPool in api/main.py uses defaults. For production, min_size/max_size should be configurable via
  settings.

  ---
  5. Testing

  5.1 Unit tests mock too much
  The unit test conftest.py mocks AsyncConnection with MagicMock(). The mock's execute().fetchone() returns factory
  data regardless of input, so tests verify routing/serialization but not query correctness. This is acceptable for
  unit tests but means integration tests carry the full correctness burden.

  5.2 Missing test scenarios:
  - No tests for unauthorized access to PUT/DELETE /user/{id} (because there's no auth — see bug 1.3)
  - No tests for invalid JWT structure/signature
  - No tests for concurrent requests or race conditions on unique constraints
  - No negative tests for meter operations with wrong user_id (another user's meter)

  5.3 Integration test cleanup is fragile (tests/integration/conftest.py)
  Fixtures create and delete test data, but if a test fails mid-way, cleanup in yield fixtures may leave stale data
  if the delete itself fails.

  ---
  6. Documentation

  6.1 README is minimal
  Missing: project purpose, API endpoint documentation, environment setup instructions, architecture overview, how
  to run with Docker.

  6.2 No docstrings on most functions
  Despite ruff being configured with pydocstyle (google convention), most functions in api/auth.py, api/models/, and
   api/routers/ lack docstrings.

  6.3 TODO.md is useful but should reference issues/tickets rather than living as a flat file.

  ---
  Priority Summary

  ┌─────────┬──────────┬─────────────────────────────────────────────────────┐
  │    #    │ Severity │                        Issue                        │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 1.3/3.1 │ CRITICAL │ User DELETE/UPDATE endpoints have no authentication │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 1.4     │ HIGH     │ Password hash exposed in API responses              │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 3.2     │ HIGH     │ .env with secrets possibly committed to git         │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 1.1     │ HIGH     │ Meter uniqueness is global, not per-user            │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 3.3     │ MEDIUM   │ No email format validation                          │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 3.5     │ MEDIUM   │ No password strength requirements                   │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 1.2     │ MEDIUM   │ DELETE returns 204 for non-existent resources       │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 1.5     │ MEDIUM   │ Rate limit too restrictive (1/min)                  │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 4.1     │ LOW      │ Missing index on meters.user_id                     │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 2.3     │ LOW      │ Logging may capture sensitive data                  │
  ├─────────┼──────────┼─────────────────────────────────────────────────────┤
  │ 6.2     │ LOW      │ Missing docstrings

- [x] limiting
- [x] routers prefixes
- [x] auth separetely
- [x] solve mypy
move invalid and expired token into unit tests?
- [x] add linter, formatter, typechecker
- [x] add db
- [x] add integration tests (separete test db)
- [x] add unit tests (mocked and patched)
- [x] add logging
- [x] logging level DEBUG only for DEV, INFO for TEST/PROD
- [x] uuid_length = 8 for DEV
- [x] pydantic-settings
- [x] split dbmodels, models and routes
- [x] pre-commit switch to make cmds
- [x] pyjwt vs jose jwt: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- [ ] respond with {entity, detail?}
- [ ] get request refactor - move return and success msg from try block to end of func

- [ ] add user auth
- [ ] add api version into url
- [ ] add health check
- [ ] rate limiting
- [ ] error handling
- [ ] test coverage 95%+
- [ ] add prometheus ?

- [ ] pydantic-settings for .env - DB_URL/ROLLBACK settings for database https://fastapi.tiangolo.com/advanced/settings/
- [x] lifespan docs https://fastapi.tiangolo.com/advanced/events/
- [ ] async tests https://fastapi.tiangolo.com/advanced/async-tests/
- [ ] sql dbs https://fastapi.tiangolo.com/tutorial/sql-databases/
- [ ] sql dbs https://sqlmodel.tiangolo.com/tutorial/fastapi/response-model/
- [ ] testing db https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#testing-database

better stack / logtail cloud logging: https://betterstack.com/community/guides/logging/logging-with-fastapi/

async SQLAlchemy x psycopg x asyncpg

SQLAlchemy: https://www.youtube.com/watch?v=cmnPiUVlIsM

asyncpg: https://magicstack.github.io/asyncpg/current/usage.html#
asyncpg: https://github.com/jordic/fastapi_asyncpg
asyncpg: https://neon.com/guides/fastapi-async
asyncpg: https://www.sheshbabu.com/posts/fastapi-without-orm-getting-started-with-asyncpg/

psycopg: https://blog.danielclayton.co.uk/posts/database-connections-with-fastapi/
psycopg: https://spwoodcock.dev/blog/2024-10-fastapi-pydantic-psycopg/
psycopg: https://medium.com/@benshearlaw/asynchronous-postgres-with-python-fastapi-and-psycopg-3-fafa5faa2c08

SQLAlchemy: https://dev.to/iambkpl/setup-fastapi-and-sqlalchemy-mysql-48m9
SQLAlchemy: https://medium.com/@suganthi2496/fastapi-with-sqlalchemy-building-scalable-apis-with-a-database-backend-7ccc9aa659a1
SQLAlchemy: https://testdriven.io/blog/fastapi-sqlmodel/

test sync x async performance

https://www.youtube.com/watch?v=cmnPiUVlIsM

## Decisions Log

### Db Engine

  1. sqlite
  2. postgresql

### Db Driver

  1. SQLAlchemy

    + easy to switch db engine (sql only)
    -- too bloated

  2. sqlmodel (=pydantic + sql alchemy wrapper)

    + FastAPI docs recommended
    - async not documented
    --- db and req/resp validation models coupled

  3. psycopg

    ++ minimal
    + sql query sanitation
    + dynamic sql query factory -> used for INSERT queries (build dynamically based on req dict keys)
    + row factory
    + sync and async
    - pg only

  4. asyncpg

    ++ even faster, than psycopg
    + sql query sanitation
    - pg only
    - async only


### Depends(db_connect) directly db_models methods args?
  E.g.: routes.py - get_meter_with_readings() - uses the same connection for both queries (Meters and Readings queries) -> One connection per one request is correct.
