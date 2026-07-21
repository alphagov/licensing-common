test: prepare
	pytest

format:
	uv run ruff check --fix && uv run ruff format

prepare:
	docker compose up -d

stop:
	docker compose down