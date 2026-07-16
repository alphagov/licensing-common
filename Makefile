test:
	cd apply_for_a_licence && pytest

format:
	uv run ruff check --fix && uv run ruff format