APP_MODULE=app.main:app
HOST=0.0.0.0
PORT=8000

PYTHON_RUN=uv run

CONTAINER_ENGINE:=$(shell if command -v podman >/dev/null 2>&1; then echo podman; elif command -v docker >/dev/null 2>&1; then echo docker; else echo ""; fi)
COMPOSE_CMD:=$(shell if command -v podman >/dev/null 2>&1; then if podman compose version >/dev/null 2>&1; then echo "podman compose"; elif command -v podman-compose >/dev/null 2>&1; then echo podman-compose; fi; elif command -v docker >/dev/null 2>&1; then echo "docker compose"; else echo ""; fi)

.DEFAULT_GOAL := help

.PHONY: help check-engine check-compose sync run dev prod compile clean \
	image-build image-run image-stop compose-up compose-down compose-logs compose-ps \
	valkey-up valkey-down

help:
	@echo "Targets:"
	@echo "  sync         Install/sync dependencies via uv"
	@echo "  run          Run API in dev mode (reload)"
	@echo "  dev          Alias for run"
	@echo "  prod         Run API with gunicorn via uv"
	@echo "  compile      Compile-check Python sources"
	@echo "  clean        Remove local virtual env and caches"
	@echo "  image-build  Build container image with Dockerfile"
	@echo "  image-run    Run container image (detached)"
	@echo "  image-stop   Stop and remove running container"
	@echo "  compose-up   Start compose stack (Podman or Docker)"
	@echo "  compose-down Stop compose stack"
	@echo "  compose-logs Follow compose logs"
	@echo "  compose-ps   Show compose services"
	@echo "  valkey-up    Start only Valkey service"
	@echo "  valkey-down  Stop and remove only Valkey service"
	@echo ""
	@echo "Detected container engine: $(if $(CONTAINER_ENGINE),$(CONTAINER_ENGINE),none)"
	@echo "Detected compose command: $(if $(COMPOSE_CMD),$(COMPOSE_CMD),none)"

check-engine:
	@if [ -z "$(CONTAINER_ENGINE)" ]; then \
		echo "No container engine found. Install podman or docker."; \
		exit 1; \
	fi

check-compose:
	@if [ -z "$(COMPOSE_CMD)" ]; then \
		echo "No compose command found. Install podman compose, podman-compose, or docker compose."; \
		exit 1; \
	fi

sync:
	$(PYTHON_RUN) python --version >/dev/null
	uv sync

run:
	$(PYTHON_RUN) uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

dev: run

prod:
	$(PYTHON_RUN) gunicorn $(APP_MODULE) -k uvicorn.workers.UvicornWorker -w 4 -b $(HOST):$(PORT) --access-logfile - --error-logfile -

compile:
	$(PYTHON_RUN) python -m compileall app

clean:
	rm -rf .venv
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

image-build: check-engine
	$(CONTAINER_ENGINE) build -t lta-datamall-bus-backend:latest .

image-run: check-engine
	$(CONTAINER_ENGINE) run -d --name lta-datamall-bus-backend --env-file .env -p 8000:8000 lta-datamall-bus-backend:latest

image-stop: check-engine
	-$(CONTAINER_ENGINE) stop lta-datamall-bus-backend
	-$(CONTAINER_ENGINE) rm lta-datamall-bus-backend

compose-up: check-compose
	$(COMPOSE_CMD) up --build -d

compose-down: check-compose
	$(COMPOSE_CMD) down

compose-logs: check-compose
	$(COMPOSE_CMD) logs -f

compose-ps: check-compose
	$(COMPOSE_CMD) ps

valkey-up: check-compose
	$(COMPOSE_CMD) up -d valkey

valkey-down: check-compose
	$(COMPOSE_CMD) stop valkey
	$(COMPOSE_CMD) rm -f valkey
