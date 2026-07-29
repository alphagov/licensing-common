.PHONY: test prepare stop format seed-db

prepare:
	uv sync

# =======================================================================
# TESTING
# =======================================================================
test: prepare-tests
	pytest

prepare-tests: prepare
	docker compose up -d

stop:
	docker compose down

# =======================================================================
# LINTING/FORMATTING
# =======================================================================
format: prepare
	uv run ruff check --fix && uv run ruff format


# =======================================================================
# DATA/SEEDING
# =======================================================================

seed-db: prepare
	uv run python -m scripts.data.seed_db
