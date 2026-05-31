# LTA DataMall Bus Backend (FastAPI)

FastAPI backend platform for LTA DataMall Bus Transport APIs, dockerized for production deployment.

## Features

- Async FastAPI service with shared `httpx` connection pool
- Valkey caching layer with graceful fallback when cache is unavailable
- Scalable runtime with Gunicorn + Uvicorn workers
- API key loaded from `.env` (`DATAMALL_API_KEY`)
- Backend port configurable via `.env` (`APP_PORT`)
- Bus Transport endpoints exposed under `/api/v1`
- Container health endpoints: `/healthz`, `/readyz`

## API Endpoints

- `GET /api/v1/bus-arrival`
- `GET /api/v1/bus-services`
- `GET /api/v1/bus-routes`
- `GET /api/v1/bus-stops`
- `GET /api/v1/passenger-volume/bus`
- `GET /api/v1/passenger-volume/od-bus`
- `GET /api/v1/planned-bus-routes`

## Local Run (without Docker)

1. Install uv (if not already installed).
2. Create `.env` from `.env.example` and set `DATAMALL_API_KEY`.
3. Sync dependencies:

```bash
uv sync
```

4. Start the app:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000} --reload
```

## Docker Run

1. Create `.env` from `.env.example` and set `DATAMALL_API_KEY`.
2. Build and run:

```bash
docker compose up --build -d
```

3. Check health:

```bash
curl http://localhost:${APP_PORT:-8000}/healthz
```

The compose stack includes a Valkey service for caching.

## Cache Configuration

Set in `.env`:

- `VALKEY_ENABLED=true`
- `VALKEY_URL=redis://valkey:6379/0`
- `VALKEY_CONNECT_TIMEOUT_SECONDS=1`
- `VALKEY_DEFAULT_TTL_SECONDS=120`
- `APP_PORT=8000`

Current cache behavior:

- Bus Arrival: 15s
- Bus Services and Bus Routes: 300s
- Bus Stops: 1800s
- Planned Bus Routes: 900s
- Passenger Volume endpoints: 21600s

## Makefile Tasks

Use `make help` to see all targets. The Makefile auto-detects Podman first, then Docker.

Common commands:

```bash
make sync
make run
make compile
make compose-up
make compose-down
make valkey-up
make valkey-down
```

## Horizontal Scaling

- Increase container replicas:

```bash
docker compose up --build --scale api=3 -d
```

- Put a load balancer or gateway in front of the replicas in production.

## Notes

- This project proxies requests to `https://datamall2.mytransport.sg/ltaodataservice`.
- Static/list APIs support `$skip` forwarding for pagination.
