---
name: backend-testing
description: "Use when adding, fixing, or reviewing backend tests for this FastAPI project, including route tests, service tests, cache behavior, and upstream error handling."
---

# Backend Testing Skill

Use this skill to design and implement robust tests for the backend API.

## Project Context

- App framework: FastAPI
- Python environment: uv
- API routes: [app/api/routes/bus.py](app/api/routes/bus.py)
- Upstream client: [app/services/lta_client.py](app/services/lta_client.py)
- Cache layer: [app/services/cache.py](app/services/cache.py)
- App wiring and lifespan: [app/main.py](app/main.py)

## Testing Goals

1. Verify endpoint behavior, input validation, and response shape.
2. Verify upstream failures are mapped to expected HTTP errors.
3. Verify cache-assisted behavior does not break correctness.
4. Keep tests deterministic with no real external API calls.

## Workflow

1. Identify the change surface and affected endpoints or services.
2. Add or update tests under a test layout that mirrors app modules.
3. Mock external dependencies:
   - Mock DataMall calls from [app/services/lta_client.py](app/services/lta_client.py).
   - Stub cache interactions from [app/services/cache.py](app/services/cache.py).
4. Cover at least these scenarios per endpoint:
   - Success response
   - Input validation failure
   - Upstream failure mapping
5. Run checks and tests with uv.
6. Keep tests readable with clear arrange, act, assert sections.

## Preferred Patterns

- Use pytest-style tests and fixtures.
- Use FastAPI test clients for route-level coverage.
- Keep one behavior assertion focus per test.
- Use explicit test data, not random values.
- Name tests with behavior intent, for example: test_bus_arrival_returns_upstream_payload.

## Commands

- Sync dependencies: make sync
- Compile check: make compile
- Run tests: uv run pytest

If pytest is not installed yet, add it to project dependencies before creating tests.

## Quality Gate Before Finish

1. New or changed behavior has corresponding tests.
2. Tests do not call live DataMall services.
3. Error handling and validation paths are covered.
4. Existing compile check still passes.
