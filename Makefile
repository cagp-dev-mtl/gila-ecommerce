ifneq ($(shell docker compose version 2>/dev/null),)
  DOCKER_COMPOSE=docker compose
else
  DOCKER_COMPOSE=docker-compose
endif

run:
	$(DOCKER_COMPOSE) up -d --build

stop:
	$(DOCKER_COMPOSE) stop

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

shell:
	$(DOCKER_COMPOSE) exec api bash

apply-migration:
	$(DOCKER_COMPOSE) exec api alembic upgrade head

create-migration:
	$(DOCKER_COMPOSE) exec api alembic revision -m "$(REVISION)"

PYTEST_RUN = $(DOCKER_COMPOSE) run --rm api-test

unit-tests:
	$(PYTEST_RUN) pytest tests/unit

functional-tests:
	$(PYTEST_RUN) pytest tests/functional

tests:
	$(PYTEST_RUN) pytest tests --cov=app --cov-report=term-missing --cov-fail-under=100

lint:
	$(DOCKER_COMPOSE) run --rm api-test ruff check app tests

.PHONY: run stop down logs ps shell apply-migration create-migration unit-tests functional-tests tests lint
