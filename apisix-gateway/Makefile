COMPOSE_CMD:=$(shell if command -v podman >/dev/null 2>&1; then if podman compose version >/dev/null 2>&1; then echo "podman compose"; elif command -v podman-compose >/dev/null 2>&1; then echo podman-compose; fi; elif command -v docker >/dev/null 2>&1; then echo "docker compose"; else echo ""; fi)

.DEFAULT_GOAL := help

.PHONY: help up down logs ps check-compose

help:
	@echo "Targets:"
	@echo "  up     Start APISIX gateway"
	@echo "  down   Stop APISIX gateway"
	@echo "  logs   Follow APISIX logs"
	@echo "  ps     Show gateway containers"
	@echo ""
	@echo "Detected compose command: $(if $(COMPOSE_CMD),$(COMPOSE_CMD),none)"

check-compose:
	@if [ -z "$(COMPOSE_CMD)" ]; then \
		echo "No compose command found. Install podman compose, podman-compose, or docker compose."; \
		exit 1; \
	fi

up: check-compose
	$(COMPOSE_CMD) up --build -d

down: check-compose
	$(COMPOSE_CMD) down

logs: check-compose
	$(COMPOSE_CMD) logs -f

ps: check-compose
	$(COMPOSE_CMD) ps
