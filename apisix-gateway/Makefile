CONTAINER_ENGINE:=$(shell if command -v podman >/dev/null 2>&1; then echo podman; elif command -v docker >/dev/null 2>&1; then echo docker; else echo ""; fi)
COMPOSE_CMD:=$(shell if command -v podman >/dev/null 2>&1; then if podman compose version >/dev/null 2>&1; then echo "podman compose"; elif command -v podman-compose >/dev/null 2>&1; then echo podman-compose; fi; elif command -v docker >/dev/null 2>&1; then echo "docker compose"; else echo ""; fi)
COMPOSE_FILE:=$(if $(filter podman,$(CONTAINER_ENGINE)),podman-compose.yml,docker-compose.yml)

.DEFAULT_GOAL := help

.PHONY: help up down logs ps check-compose

help:
	@echo "Targets:"
	@echo "  up     Start APISIX, etcd, dashboard, and route bootstrap"
	@echo "  down   Stop the full gateway stack"
	@echo "  logs   Follow gateway stack logs"
	@echo "  ps     Show gateway stack containers"
	@echo ""
	@echo "Detected container engine: $(if $(CONTAINER_ENGINE),$(CONTAINER_ENGINE),none)"
	@echo "Detected compose command: $(if $(COMPOSE_CMD),$(COMPOSE_CMD),none)"
	@echo "Selected compose file: $(COMPOSE_FILE)"

check-compose:
	@if [ -z "$(COMPOSE_CMD)" ]; then \
		echo "No compose command found. Install podman compose, podman-compose, or docker compose."; \
		exit 1; \
	fi

up: check-compose
	$(COMPOSE_CMD) -f $(COMPOSE_FILE) up --build -d

down: check-compose
	$(COMPOSE_CMD) -f $(COMPOSE_FILE) down

logs: check-compose
	$(COMPOSE_CMD) -f $(COMPOSE_FILE) logs -f

ps: check-compose
	$(COMPOSE_CMD) -f $(COMPOSE_FILE) ps
