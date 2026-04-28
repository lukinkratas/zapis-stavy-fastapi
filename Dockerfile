FROM python:3.11-alpine AS builder

RUN apk update && apk upgrade --no-cache

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1
# Pre-compiles .py files to .pyc at build time -> you faster container startup
ENV UV_COMPILE_BYTECODE=1

# cd
WORKDIR /zapis-stavy-fastapi

# Copy the project into the image
COPY pyproject.toml uv.lock ./

# Sync the project into a new environment, asserting the lockfile is up to date
RUN uv sync --locked --no-install-project

# ----- PROD stage -----
FROM python:3.11-alpine AS prod

RUN apk update && apk upgrade --no-cache

# cd
WORKDIR /zapis-stavy-fastapi

# Add non-root user
RUN adduser -D appuser

COPY --chown=appuser:appuser api api
COPY --chown=appuser:appuser --from=builder /zapis-stavy-fastapi/.venv .venv

RUN mkdir -p logs && chown appuser:appuser logs

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://127.0.0.1:8080/health || exit 1

# start the server
CMD ["/zapis-stavy-fastapi/.venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
