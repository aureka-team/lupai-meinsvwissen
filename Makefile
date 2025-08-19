.PHONY: core-build devcontainer-build api-build


core-build:
	docker compose build lupai-mw-core

core-run: core-build
	docker compose run --rm lupai-mw-core


devcontainer-build: core-build
	docker compose -f .devcontainer/docker-compose.yml build lupai-mw-devcontainer


redis-start:
	docker compose up -d lupai-mw-redis

redis-stop:
	docker compose stop lupai-mw-redis

redis-flush:
	docker compose exec lupai-mw-redis redis-cli FLUSHALL

redis-restart: redis-stop redis-start


mongo-start:
	docker compose up -d lupai-mw-mongo

mongo-stop:
	docker compose stop lupai-mw-mongo

mongo-restart: mongo-stop mongo-start


qdrant-start:
	docker compose up -d lupai-mw-qdrant

qdrant-stop:
	docker compose stop lupai-mw-qdrant

qdrant-restart: qdrant-stop qdrant-start


api-build: core-build
	docker compose build lupai-mw-api

api-run: api-build
	docker compose run --rm lupai-mw-api

api-up: api-build
	docker compose up lupai-mw-api -d

api-stop:
	docker compose stop lupai-mw-api

api-restart: api-stop api-up


mcp-build:
	docker compose build lupai-mw-mcp

mcp-run: mcp-build
	docker compose  run --rm lupai-mw-mcp

mcp-up: mcp-build
	docker compose up -d lupai-mw-mcp

mcp-stop:
	docker stop lupai-mw-mcp

mcp-restart: mcp-stop mcp-up


create-qdrant-collections: devcontainer-build
	docker compose -f .devcontainer/docker-compose.yml run --rm --entrypoint="python -m lupai_mw.scripts.qdrant.create_collections" lupai-mw-devcontainer
