.PHONY: fmt lint lint-fix typechk test test-int test-all clean-up serve-dev build

help:
	@echo "Available targets:"
	@echo "  fmt              - Format the code using Ruff"
	@echo "  lint             - Check linting of the code using Ruff"
	@echo "  lint-fix         - Check and fix linting if the code using Ruff"
	@echo "  typechk          - Type check the code using mypy"
	@echo "  clean-up         - Clean up"
	@echo "  test             - Run unit tests"
	@echo "  test-int         - Run ingtegration tests"
	@echo "  test-cov         - Run all tests with html coverage"
	@echo "  serve-dev        - Serve the application with reloading"
	@echo "  build            - Build docker image"
	@echo "  help             - Show this help message"

fmt:
	uv run --dev ruff format
	terraform fmt terraform/

lint:
	uv run --dev ruff check
	uv run --dev sqlfluff lint --dialect postgres sql/

lint-fix:
	uv run --dev ruff check --fix
	uv run --dev sqlfluff fix --dialect postgres  sql/

typechk:
	uv run --dev mypy .

test:
	uv run --dev pytest tests/unit -vv -p no:warnings --cov=api --cov-report=term-missing --cov-branch

test-int:
	uv run --dev pytest tests/integration -vv -p no:warnings --cov=api --cov-report=term-missing --cov-branch

test-cov:
	uv run --dev pytest -vv -p no:warnings --cov=api --cov-report=term-missing --cov-branch --cov-fail-under=95 --cov-report=html:htmlcov

clean-up:
	rm -rvf .coverage htmlcov logs/api.log*

serve-dev:
	uv run uvicorn api.main:app --reload

build:
	docker build . -t zapis-stavy-fastapi-api