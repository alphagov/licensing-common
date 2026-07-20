test: prepare
	cd apply_for_a_licence && pytest
	make kill-db

format:
	uv run ruff check --fix && uv run ruff format

prepare:
	docker run -d -p 10260:10260 --name docdb ghcr.io/documentdb/documentdb/documentdb-local:latest \
	--username demo --password test

kill-db:
	docker kill docdb && docker rm docdb