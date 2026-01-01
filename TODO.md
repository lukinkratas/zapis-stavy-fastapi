2. Use conn.execute? https://www.psycopg.org/psycopg3/docs/advanced/pool.html
```
async with AsyncConnectionPool(...) as pool:
    async with pool.connection() as conn:
        await conn.execute("SELECT something FROM somewhere ...")

        async with conn.cursor() as cur:
            await cur.execute("SELECT something else...")
```

- [x] add linter, formatter, typechecker
- [x] add db
- [x] solve pcr
- [ ] solve mypy
- [ ] add integration tests (separete test db)
- [ ] add unit tests (mocked and patched)
- [ ] add logging

```
from testcontainers.postgres import PostgresContainer
import psycopg
import pytest

@pytest.fixture
def db():
    with PostgresContainer("postgres:16") as postgres:
        conn = psycopg.connect(postgres.get_connection_url())
        yield conn
        conn.close()
```
- [ ] add user auth
- [ ] add api version into url
- [ ] add health check
- [ ] rate limiting
- [ ] error handling
- [ ] add prometheus ?
- [ ] fix err:
/Users/lukaskratochvila/projects/zapis-stavy-backend/.venv/lib/python3.12/site-packages/psycopg_pool/pool_async.py:163: RuntimeWarning: opening the async pool AsyncConnectionPool in the constructor is deprecated and will not be supported anymore in a future release. Please use `await pool.open()`, or use the pool as context manager using: `async with AsyncConnectionPool(...) as pool: `...

https://youtu.be/GMBiCMsEsq8?si=b9dgLTg5oUNSKUYB
- [ ] pydantic-settings? e.g.: loggin level?

- [ ] pydantic-settings for .env - DB_URL/ROLLBACK settings for database https://fastapi.tiangolo.com/advanced/settings/
- [x] lifespan docs https://fastapi.tiangolo.com/advanced/events/
- [ ] async tests https://fastapi.tiangolo.com/advanced/async-tests/
- [ ] sql dbs https://fastapi.tiangolo.com/tutorial/sql-databases/
- [ ] sql dbs https://sqlmodel.tiangolo.com/tutorial/fastapi/response-model/
- [ ] testing db https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#testing-database

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
