yield async_client, mock_conn, mock_cursor
solve mypy

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
