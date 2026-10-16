.PHONY: test prepare stop format seed_db_from_bson_files syncseed_db_from_mongodb_archive_file

prepare: sync

sync:
	uv sync --active

docker-compose:
	mise exec -- docker compose up -d
# =======================================================================
# TESTING
# =======================================================================
test: prepare-tests
	pytest

prepare-tests: prepare docker-compose


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

seed_db_from_bson_files: prepare
	uv run python -m scripts.data.seed_db_from_bson_files

seed_db_from_mongodb_archive_file: prepare
	uv run python -m scripts.data.seed_db_from_mongodb_archive_file
