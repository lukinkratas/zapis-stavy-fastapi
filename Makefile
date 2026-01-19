.PHONY: install install-all install-dev fmt lint lint-fix typechk test test-int test-all clean-up serve-dev

help:
	@echo "Available targets:"
	@echo "  install          - Install the package and its dependencies"
	@echo "  install-all      - Install the package with all extras"
	@echo "  install-dev      - Install the package with dev dependencies"
	@echo "  fmt              - Format the code using Ruff"
	@echo "  lint             - Check linting of the code using Ruff"
	@echo "  lint-fix         - Check and fix linting if the code using Ruff"
	@echo "  typechk          - Type check the code using mypy"
	@echo "  clean-up         - Clean up"
	@echo "  test             - Run unit tests"
	@echo "  test-int         - Run ingtegration tests"
	@echo "  test-int         - Run all tests with html coverage"
	@echo "  serve-dev        - Serve the application with reloading"
	@echo "  help             - Show this help message"

install:
	uv sync

install-all:
	uv sync --all-extras

install-dev:
	uv sync --group dev

fmt:
	uv run --dev ruff format

lint:
	uv run --dev ruff check

lint-fix:
	uv run --dev ruff check --fix

typechk:
	uv run --dev mypy .

test:
	uv run --dev pytest tests/unit -vv -p no:warnings --cov=api --cov-report=term-missing --cov-branch

test-int:
	uv run --dev pytest tests/integration -vv -p no:warnings --cov=api --cov-report=term-missing --cov-branch

test-all:
	uv run --dev pytest tests/ -vv -p no:warnings --cov=api --cov-report=term-missing --cov-branch --cov-fail-under=95 --cov-report=html:htmlcov

clean-up:
	rm -rvf .coverage htmlcov api.log*

serve-dev:
	uv run uvicorn api.main:app --reload
