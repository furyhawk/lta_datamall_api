# LTA DataMall APISIX Gateway

This project runs Apache APISIX as an API gateway in front of the LTA DataMall FastAPI backend.

## What it does

- Proxies `/api/v1/*` to the backend service
- Forwards backend health and docs endpoints through the gateway
- Keeps gateway configuration isolated from the API service project

## Prerequisites

- Docker or Podman with compose support
- The backend service running on `http://host.docker.internal:8068` on macOS

If your backend runs on a different host or port, update the upstream target in [conf/apisix.yaml](conf/apisix.yaml).

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

## Ports

- `9080` - APISIX proxy listener
