# Zapis Stavy Backend [WIP]

FastAPI + Postgres via Psycopg app.

```sh
# build
make build
# deploy
docker compose up -d
```

## Decisions Log

### DB

  1. sqlite

  2. postgresql

  choice: postgresql

### DB Driver

  1. psycopg
    + + minimal
    + sql query sanitation
    + dynamic sql query factory -> used for INSERT queries (build dynamically based on req dict keys)
    + row factory
    + sync and async
    - pg only

  2. asyncpg
    + + even faster, than psycopg
    + sql query sanitation
    - pg only
    - async only


### ORM or not

  1. sqlmodel (=pydantic + sql alchemy wrapper)
    + FastAPI docs recommended
    - async not documented
    - - - db and req/resp validation models coupled

  2. SQLAlchemy
    + easy to switch db engine (sql only)
    + handles security
    - subjective: session abstraction mental model (session.add, commit, rollback)

  3. No ORM
    + no bloat
    + SQL-like queries and db cmds (commit, rollback, etc.)
    - security

  choice: no ORM - totally sufficient, yet minimal

### Dockerfile base image

  1. alpine
    + tiny
    + reducing attack surface and pull times
  
  2. slim-trixie - use if glibc is needed (numpy, pandas, psycopg2, alpine uses musl libc)

  choice: alpine - bcs of its' benefits and glibc not being used

### Row class returned from db

  1. dict_row
    - too much overhead
    - dict methods are not really utilized in the api
    - fields not static typed

  2. namedtuple_row
    - very small overhead
    - fields not static typed

  3. custom namedtuple row
    + very small overhead
    + immutable

  4. custom dataclass row
    + extensible
    + inheritance
    + mutable/immutable (frozen=True)
    + way to lower overhead (slots=True)

  5. custom typeddict row

  choice: custom namedtuple row - totally sufficient, yet minimal overhead

### DB ID

  1. incerement ID
    + appending record into page does not need to re-index
    - insecure direct object reference
    - servers attempting to insert record with the same ID

  2. UUID v4
    + random
    - "page split" - need to re-index, when new record is inserted

  3. UUID v7
    + random
    + first half is unix timestamp - avoids page splits
    - need to update database to pg18

  choice: UUID v7 - bcs of its' benefits

### Postgres version

  1. v14 - initial

  2. v18
    + UUID v7

  choice: v18 - bcs of UUID v7

### ENV vars config

  1. pydantic-settings
    + centralized
    + variables validation, unless extra=ignore
    + type validation - not really utilized in this backend
    - nested configs - not really usable, required __
    + lru_cached get_settings in theory works great with FastAPI's dependency injection system, however for example for db settings, this cannot be cleanly utilized in combination with psycopg connection pool (not an endpoint dependency -> no auto execution -> has to be mocked anyway and not dependency overriden)

  2. python-dotenv
    + also centralized

  choice: python-dotenv - totally sufficient, can be changed to pydantic-settings, once it's relly utilized

## Resources

better stack / logtail cloud logging: https://betterstack.com/community/guides/logging/logging-with-fastapi/

asyncpg: https://magicstack.github.io/asyncpg/current/usage.html#
asyncpg: https://github.com/jordic/fastapi_asyncpg
asyncpg: https://neon.com/guides/fastapi-async
asyncpg: https://www.sheshbabu.com/posts/fastapi-without-orm-getting-started-with-asyncpg/

psycopg: https://blog.danielclayton.co.uk/posts/database-connections-with-fastapi/
psycopg: https://spwoodcock.dev/blog/2024-10-fastapi-pydantic-psycopg/
psycopg: https://medium.com/@benshearlaw/asynchronous-postgres-with-python-fastapi-and-psycopg-3-fafa5faa2c08
psycopg: https://blog.danielclayton.co.uk/posts/database-connections-with-fastapi/

SQLAlchemy: https://www.youtube.com/watch?v=cmnPiUVlIsM

SQLAlchemy sync: https://dev.to/iambkpl/setup-fastapi-and-sqlalchemy-mysql-48m9
SQLAlchemy sync: https://medium.com/@suganthi2496/fastapi-with-sqlalchemy-building-scalable-apis-with-a-database-backend-7ccc9aa659a1

SQLAlchemy sync: https://youtu.be/XlnmN4BfCxw?si=tuJ2S9PpxMOhF-pM
SQLAlchemy sync: https://github.com/ArjanCodes/examples/tree/main/2023/fastapi-router

SQLAlchemy async: https://youtu.be/SR5NYCdzKkc?si=rvkNPMpGO_KLbDn9
SQLAlchemy async: https://github.com/techwithtim/FastAPIPhotoVideoSharing

SQLModel: https://testdriven.io/blog/fastapi-sqlmodel/

test sync x async performance

https://www.youtube.com/watch?v=cmnPiUVlIsM

Dockerfile https://github.com/ArjanCodes/examples/blob/main/2025/efficient-python-dockerfile/Dockerfile.10_final
