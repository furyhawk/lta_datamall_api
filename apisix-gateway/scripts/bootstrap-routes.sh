#!/bin/sh

set -eu

ADMIN_URL="${APISIX_ADMIN_URL:-http://apisix:9180}"
ADMIN_KEY="${APISIX_ADMIN_KEY:?APISIX_ADMIN_KEY is required}"
BACKEND_HOST="${BACKEND_HOST:?BACKEND_HOST is required}"
BACKEND_PORT="${BACKEND_PORT:-8068}"

request() {
  method="$1"
  path="$2"
  data="$3"

  http_code=$(curl -sS -o /tmp/apisix-bootstrap-response.json -w "%{http_code}" \
    -X "$method" \
    -H "X-API-KEY: $ADMIN_KEY" \
    -H "Content-Type: application/json" \
    "$ADMIN_URL$path" \
    -d "$data")

  if [ "$http_code" -lt 200 ] || [ "$http_code" -ge 300 ]; then
    echo "APISIX admin request failed for $path with status $http_code"
    cat /tmp/apisix-bootstrap-response.json
    exit 1
  fi
}

echo "Waiting for APISIX Admin API at $ADMIN_URL"
for _ in $(seq 1 60); do
  if curl -fsS -H "X-API-KEY: $ADMIN_KEY" "$ADMIN_URL/apisix/admin/routes" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! curl -fsS -H "X-API-KEY: $ADMIN_KEY" "$ADMIN_URL/apisix/admin/routes" >/dev/null 2>&1; then
  echo "APISIX Admin API did not become ready in time"
  exit 1
fi

echo "Seeding upstream and routes"

request PUT /apisix/admin/upstreams/1 "{\"id\":\"1\",\"type\":\"roundrobin\",\"nodes\":{\"${BACKEND_HOST}:${BACKEND_PORT}\":1}}"
request PUT /apisix/admin/routes/1 '{"id":"1","uri":"/healthz","upstream_id":"1"}'
request PUT /apisix/admin/routes/2 '{"id":"2","uri":"/readyz","upstream_id":"1"}'
request PUT /apisix/admin/routes/3 '{"id":"3","uri":"/openapi.json","upstream_id":"1"}'
request PUT /apisix/admin/routes/4 '{"id":"4","uri":"/docs","upstream_id":"1"}'
request PUT /apisix/admin/routes/5 '{"id":"5","uri":"/redoc","upstream_id":"1"}'
request PUT /apisix/admin/routes/6 '{"id":"6","uri":"/api/v1/*","upstream_id":"1"}'

echo "APISIX bootstrap complete"