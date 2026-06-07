# LTA DataMall APISIX Gateway

This project runs Apache APISIX as an API gateway in front of the LTA DataMall FastAPI backend.

## What it does

- Proxies `/api/v1/*` to the backend service
- Forwards backend health and docs endpoints through the gateway
- Keeps gateway configuration isolated from the API service project

## Prerequisites

- Docker or Podman with compose support
- The backend service running on `http://host.docker.internal:8068` on macOS

Docker uses `host.docker.internal`.
Podman uses `host.containers.internal`.

This project keeps separate compose wiring for each runtime and the gateway `Makefile` selects the right file automatically.

If your backend runs on a different host or port, update the upstream target in [conf/apisix.yaml](conf/apisix.yaml) for Docker or [conf/apisix.podman.yaml](conf/apisix.podman.yaml) for Podman.

## Run

1. Start the backend service first.
2. Start the gateway:

```bash
make up
```

3. Send requests through APISIX:

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
