# LTA DataMall APISIX Gateway

This project runs Apache APISIX as an API gateway in front of the LTA DataMall FastAPI backend.

## What it does

- Proxies `/api/v1/*` to the backend service
- Forwards backend health and docs endpoints through the gateway
- Exposes Apache APISIX Dashboard for route inspection and editing
- Keeps gateway configuration isolated from the API service project

## Prerequisites

- Docker or Podman with compose support
- The backend service running on `http://host.docker.internal:8068` on macOS

Docker uses `host.docker.internal`.
Podman uses `host.containers.internal`.

This project keeps separate compose wiring for each runtime and the gateway `Makefile` selects the right file automatically.

If your backend runs on a different host or port, update `BACKEND_HOST` and `BACKEND_PORT` in the selected compose file.

## Run

1. Start the backend service first.
2. Start the gateway:

```bash
make up
```

3. Open the dashboard:

```bash
open http://localhost:9099
```

Dashboard default login:

- Username: `admin`
- Password: `admin`

4. Send requests through APISIX:

```bash
curl "http://localhost:9080/api/v1/bus-arrival?BusStopCode=83139&ServiceNo=3&Date=2025-01-01"
```

## Useful Commands

```bash
make up
make down
make logs
make ps
```

`make up`, `make down`, `make logs`, and `make ps` automatically choose `docker-compose.yml` for Docker and `podman-compose.yml` for Podman.

## Ports

- `9080` - APISIX proxy listener
- `9180` - APISIX Admin API
- `9099` - APISIX Dashboard

## Notes

- This stack uses APISIX traditional mode with etcd so the dashboard can manage routes.
- The initial upstream and routes are seeded automatically by `scripts/bootstrap-routes.sh` when the stack starts.
- `conf/apisix.yaml` and `conf/apisix.podman.yaml` are kept only as standalone-mode references and are not loaded by the dashboard-enabled stack.
- Change the default dashboard login and the Admin API key before using this outside local development.

