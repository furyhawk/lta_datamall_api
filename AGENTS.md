# AGENTS

Guidance for AI coding agents working in this repository.

## Project Snapshot

- Purpose: FastAPI backend proxy for LTA DataMall Bus Transport APIs.
- Runtime: Python 3.12 with uv-managed environment.
- Container: Podman or Docker via compose.
- API docs source: [docs/LTA_DataMall_API_User_Guide.pdf](docs/LTA_DataMall_API_User_Guide.pdf)
- OpenAPI reference: [openapi.json](openapi.json)

## First Commands To Run

- Install dependencies: make sync
- Compile check: make compile
- Run local dev server: make run
- Show available targets: make help

If Make targets are unavailable, use direct uv commands from [README.md](README.md).

## Build, Run, and Ops Commands

- Dependency sync: make sync
- Dev server with reload: make run
- Production server: make prod
- Compile check: make compile
- Compose up: make compose-up
- Compose down: make compose-down
- Compose logs: make compose-logs
- Compose services: make compose-ps

No test or lint targets are defined yet.

## Required Environment

- Required env var: DATAMALL_API_KEY
- Local env file: [.env](.env)
- Template: [.env.example](.env.example)
- Ignore rule already set in [.gitignore](.gitignore)

The app fails to start if DATAMALL_API_KEY is missing.

## Architecture Map

- App entrypoint and lifespan wiring: [app/main.py](app/main.py)
- Settings and env loading: [app/core/config.py](app/core/config.py)
- Upstream HTTP client wrapper: [app/services/lta_client.py](app/services/lta_client.py)
- Valkey cache client wrapper: [app/services/cache.py](app/services/cache.py)
- Bus API routes: [app/api/routes/bus.py](app/api/routes/bus.py)
- Health routes: [app/api/routes/health.py](app/api/routes/health.py)
- Container build: [Dockerfile](Dockerfile)
- Compose deployment: [docker-compose.yml](docker-compose.yml)

## Coding Conventions For This Repo

- Keep endpoint namespace under /api/v1.
- Preserve upstream query parameter names using aliases such as BusStopCode, ServiceNo, Date, and $skip.
- Route handlers return upstream JSON payloads directly unless feature work requires transformation.
- Keep cache reads/writes inside route helper flow; do not duplicate cache key logic across handlers.
- Centralize outbound DataMall logic in [app/services/lta_client.py](app/services/lta_client.py), not inside routes.
- Add new environment variables in [app/core/config.py](app/core/config.py) and document them in [.env.example](.env.example).

## Change Safety Checklist

Before finishing edits:

- Run make compile
- If Docker or Podman is available, run make compose-up and verify health endpoint
- Ensure [.env](.env) is not modified with secrets intended for commit
- Update [README.md](README.md) when commands, routes, or behavior changes

## Known Gaps

- No automated tests yet
- No lint or format tooling configured
- [app/schemas](app/schemas) currently has no domain models

When adding major features, consider adding tests and response schemas.
