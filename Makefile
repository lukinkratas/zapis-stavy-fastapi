.PHONY: install install-all install-dev format lint lint-fix typecheck test test-int clean-up serve-dev

help:
	@echo "Available targets:"
	@echo "  install          - Install the package and its dependencies"
	@echo "  install-all      - Install the package with all extras"
	@echo "  install-dev      - Install the package with dev dependencies"
	@echo "  format           - Format the code using Ruff"
	@echo "  lint             - Check linting of the code using Ruff"
	@echo "  lint-fix         - Check and fix linting if the code using Ruff"
	@echo "  typecheck        - Type check the code using mypy"
	@echo "  clean-up         - Clean up"
	@echo "  test             - Run tests"
	@echo "  test             - Run ingtegration tests"
	@echo "  serve-dev        - Serve the application with reloading"
	@echo "  help             - Show this help message"

install:
	uv sync

install-all:
	uv sync --all-extras

install-dev:
	uv sync --group dev

format:
	uv run --dev ruff format

lint:
	uv run --dev ruff check

lint-fix:
	uv run --dev ruff check --fix

typecheck:
	uv run --dev mypy .

test:
	uv run --dev pytest tests/unit -vv -p no:warnings --cov=zapisstavyapi --cov-report=term-missing --cov-branch

test-int:
	uv run --dev pytest tests/integration -vv -p no:warnings --cov=zapisstavyapi --cov-report=term-missing --cov-branch

clean-up:
	rm -rvf .coverage

serve-dev:
	uv run uvicorn zapisstavyapi.main:app --reload
