# LTA DataMall Bus Backend (FastAPI)

FastAPI backend platform for LTA DataMall Bus Transport APIs, dockerized for production deployment.

## Features

- Async FastAPI service with shared `httpx` connection pool
- Scalable runtime with Gunicorn + Uvicorn workers
- API key loaded from `.env` (`DATAMALL_API_KEY`)
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
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Run

1. Create `.env` from `.env.example` and set `DATAMALL_API_KEY`.
2. Build and run:

```bash
docker compose up --build -d
```

3. Check health:

```bash
curl http://localhost:8000/healthz
```

## Makefile Tasks

Use `make help` to see all targets. The Makefile auto-detects Podman first, then Docker.

Common commands:

```bash
make sync
make run
make compile
make compose-up
make compose-down
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
