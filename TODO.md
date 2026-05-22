- [ ] phase 1 works locally

- [x] add e2e testing
- [x] review e2e postman collection
- [x] user endpoints with access token
- [x] login and register - same form -> Nope
- [x] DEL/PUT endpoints - user_id from JWT token, not in endpoint name
- [x] confirmed only in authorize, or in get_current_user as is in fast api docs? -> get_current_user + get_current_confirmed_user -> allow to login and resend confirmation token
- [x] split create and delete tests in unit tests
- [x] refactor int tests
- [x] refactor unit tests
- [x] tests update - every token dependent endpoint test with valid, expired, random_id_token
- [x] tests for deleting, updating non existing and foregin user data
- [x] tests update - every user dependent endpoint test with confirmed and not confirmed user
- [x] test pydantic validations
- [x] test classes per endpoint? TestUpdate, TestCreateAndDelete, etc.
- [x] distinguish between other_user_access_token and not_registered_user_access_token -> test other_user registered
- [x] database / tables assertions
- [x] review coverage
- [x] Dockerfile
- [x] register endpoint user field returns password bug
- [x] remove logtail, add AWS logs like logtail (CloudWatch -> watchtower)
- [x] api version in the name
- [x] use detail everywhere possible
- [x] rename credentials to creds
- [x] move auth helpers out of routers
- [x] services folder as an extra layer between routers and models
- [x] log func - do not logs args, kwargs, bcs of PIIs
- [x] db_conn.commit() needed in conftest?
- [x] keep db_conn: Annotated[AsyncConnection, Depends(connect_to_db)] on routers lvl or ~~move to services lvl~~ NOT (keep service layer independent of fastapi dependencies)?
- [x] are logs for API (info lvl) needed, or already handled by default fastapi logging well?
- [x] bruno collection instead of postman
- [x] docker_db fixture in conftest
- [x] tests async backend asyncio instd of anyio
- [x] app state connection pool?
- [x] common.sql not needed?
- [x] bruno collection
- [x] module docstrings
- [x] services docstrings
- [x] psycopg row factory - dataclass / namedtuple / typeddict
- [x] sqlfluff for sql linting - CI, Makefile? as part of make lint, make fmt
- [x] terraform fmt as park of make fmt
- [x] services logging
- [x] use uuid v7
- [x] return pydantic models
- [x] prod: remove confirmation url from register response json

- [ ] pydantic-settings?

- [ ] logging lvl debug in all other places? + debug only used in dev?

- [ ] services.users.register_user -> services.users.register + from api.services import users as users_service + users_service.register

- [ ] services and models create/register(email, password) x update(data) + same for location - unify - either use dynamic or hardcoded fields in both.
  - [ ] if dynamic fields: allowed fields in models
  ```
    ALLOWED_UPDATE_FIELDS = {"email", "password"}

    invalid = set(data) - ALLOWED_UPDATE_FIELDS
    if invalid:
        raise ValueError(f"Invalid fields: {invalid}")
  ```

- [ ] fix GH actions
- [ ] fix pre-commit
- [ ] CICD - dev/test/prod branches + make test-cov in test branch
- [ ] CORS middleware?
- [ ] hardcode email and password in UsersTable model? -> Update still dynamic or also hardcoded?

- [ ] prod: no file logging (diff between dev and prod)

- [ ] upload pic
- [ ] LLM advisory + langfuse observability
- [ ] test latency with sqlaclehmy ORM - prev issue engine, sessionmaker, dbsession model in tests

- [ ] test with sqlalchemy

- [x] switch from meters to locations
- [x] use confirmation token
- [x] testcontainers for integration tests
- [x] id as sub for access token and confirmation token -> confirmation token update table without get_user middle step, be careful with get_uset + authenticate user (comes with email from web form)

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

- [x] add user auth
- [ ] add api version into url
- [x] add health check
- [x] rate limiting
- [ ] error handling
- [x] test coverage 95%+
- [ ] add prometheus ?

better stack / logtail cloud logging: https://betterstack.com/community/guides/logging/logging-with-fastapi/

async SQLAlchemy x psycopg x asyncpg

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

### Dockerfile base image

  1. alpine
    + tiny
    + reducing attack surface and pull times
  
  2. slim-trixie - use if glibc is needed (numpy, pandas, psycopg2, alpine uses musl libc)

  choice: alpine

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

  choice: custom namedtuple row

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

### Postgres version

  1. v14 - initial
  2. v18

    + UUID v7

  choice: v18

### ENV vars config

  1. python-dotenv

  2. pydantic-settings

    + variables validation
    + type validation
    + centralized
    + nested configs
