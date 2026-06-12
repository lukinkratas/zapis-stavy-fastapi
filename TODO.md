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
- [x] prod: no file logging (diff between dev and prod)
- [x] add user auth
- [x] add api version into url
- [x] add health check
- [x] rate limiting
- [x] error handling
- [x] test coverage 95%+
- [x] test branch with sqlalchemy
- [x] test branch with pydantic-settings
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
- [x] respond with {entity, detail?}
- [x] tf gh action
- [x] settings for tests mocked - AWS creds, DB settings, JWT settings are not really needed
- [x] implement ENV = test: logging_config

- [ ] pydantic-settings + dependency overriden in tests
  - [ ] Settings - ENV
  - [ ] DbSettings - DB_NAME, DB_USERNAME, DB_PASSWORD
    - api.db.get_conn_info
  - [ ] JwtSettings - JWT_SECRET_KEY
    - api.auth._create_jwt_token
      -> create_access_token -> /auth/login
      -> create_confirmation_token -> /users/register
    - api.auth._get_sub
      -> get_current_user > /users/update and /users/delete
      -> /auth/confirm
  - [ ] AwsSettings - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME
    - ap.aws.session
      -> ses_send_email -> routers.users._send_confirmation_email -> /users/register

- [ ] _get_sub -> get_sub
- [ ] add /api/ in the app

- [ ] fix GH actions
- [ ] fix pre-commit
- [ ] CICD - dev/test/prod branches + make test-cov in test branch
- [ ] CORS middleware?
- [ ] hardcode email and password in UsersTable model? -> Update still dynamic or also hardcoded?

- [ ] services.users.register_user -> services.users.register + from api.services import users as users_service + users_service.register

- [ ] services and models create/register(email, password) x update(data) + same for location - unify - either use dynamic or hardcoded fields in both.
  - [ ] if dynamic fields: allowed fields in models
  ```
    ALLOWED_UPDATE_FIELDS = {"email", "password"}

    invalid = set(data) - ALLOWED_UPDATE_FIELDS
    if invalid:
        raise ValueError(f"Invalid fields: {invalid}")
  ```

- [ ] upload pic
- [ ] LLM advisory + langfuse observability
- [ ] test latency with sqlaclehmy ORM - prev issue engine, sessionmaker, dbsession model in tests
- [ ] prod: add prometheus ?
