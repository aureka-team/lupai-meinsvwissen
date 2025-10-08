.PHONY: core-build devcontainer-build api-build


core-build:
	[ -e .env ] || touch .env
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

api-start: api-build
	docker compose up lupai-mw-api -d

api-stop:
	docker compose stop lupai-mw-api

api-restart: api-stop api-start


mcp-build: core-build
	docker compose build lupai-mw-mcp

mcp-start: mcp-build
	docker compose up -d lupai-mw-mcp

mcp-stop:
	docker stop lupai-mw-mcp

mcp-restart: mcp-stop mcp-start


create-qdrant-collections: devcontainer-build
	docker compose -f .devcontainer/docker-compose.yml run --rm --entrypoint="python -m lupai_mw.scripts.qdrant.create_collections" lupai-mw-devcontainer

run-test-queries: devcontainer-build
	docker compose -f .devcontainer/docker-compose.yml run --rm --entrypoint="python -m lupai_mw.scripts.multi_agent.run_test_queries" lupai-mw-devcontainer

test-chat: devcontainer-build
	docker compose -f .devcontainer/docker-compose.yml run --rm --entrypoint="python -m lupai_mw.scripts.chat.test_chat" lupai-mw-devcontainer

test-websocket: devcontainer-build
	docker compose -f .devcontainer/docker-compose.yml run --rm --entrypoint="python -m lupai_mw.scripts.websocket.test_websocket" lupai-mw-devcontainer
