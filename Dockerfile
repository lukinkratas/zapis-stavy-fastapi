FROM python:3.11.0

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

# Copy the project into the image
COPY . /api

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /api
RUN uv sync --locked

# start the server
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
