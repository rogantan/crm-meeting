.PHONY: all up test

all: up test

up:
	docker compose -f docker/docker-compose.yml up --build

test:
	poetry run pytest
