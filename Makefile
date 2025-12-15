.PHONY: serve-dev

help:
	@echo "Available targets:"
	@echo "  serve-dev - Serve the application with reloading"
	@echo "  help      - Show this help message"

serve-dev:
	uv run uvicorn zapis_stavy_api.main:app --reload
