from typing import Any

import httpx

from app.api.routes.bus import get_cache_client, get_lta_client
from app.services.cache import CacheClient


class StubLTAClient:
    def __init__(self, payload: dict[str, Any] | None = None, error: Exception | None = None):
        self.payload = payload if payload is not None else {"value": []}
        self.error = error
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append((path, params))
        if self.error is not None:
            raise self.error
        return self.payload


class StubCacheClient:
    def __init__(self, initial: dict[str, Any] | None = None):
        self._store = initial if initial is not None else {}
        self.set_calls: list[tuple[str, dict[str, Any], int | None]] = []

    @staticmethod
    def build_cache_key(path: str, params: dict[str, Any] | None = None) -> str:
        return CacheClient.build_cache_key(path, params)

    async def get_json(self, key: str) -> dict[str, Any] | None:
        return self._store.get(key)

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        self._store[key] = value
        self.set_calls.append((key, value, ttl_seconds))


def _override_clients(app, lta_client: StubLTAClient, cache_client: StubCacheClient) -> None:
    async def _lta_override():
        return lta_client

    async def _cache_override():
        return cache_client

    app.dependency_overrides[get_lta_client] = _lta_override
    app.dependency_overrides[get_cache_client] = _cache_override


def test_bus_arrival_returns_upstream_payload(app, client):
    upstream_payload = {"value": [{"ServiceNo": "10"}]}
    lta_client = StubLTAClient(payload=upstream_payload)
    cache_client = StubCacheClient()
    _override_clients(app, lta_client, cache_client)

    response = client.get("/api/v1/bus-arrival", params={"BusStopCode": "12345", "ServiceNo": "10"})

    assert response.status_code == 200
    assert response.json() == upstream_payload
    assert lta_client.calls == [("/v3/BusArrival", {"BusStopCode": "12345", "ServiceNo": "10"})]
    assert len(cache_client.set_calls) == 1
    assert cache_client.set_calls[0][2] == 15


def test_bus_arrival_rejects_invalid_bus_stop_code(app, client):
    lta_client = StubLTAClient(payload={"value": []})
    cache_client = StubCacheClient()
    _override_clients(app, lta_client, cache_client)

    response = client.get("/api/v1/bus-arrival", params={"BusStopCode": "1234"})

    assert response.status_code == 422
    assert lta_client.calls == []


def test_bus_arrival_uses_cache_and_skips_upstream_call(app, client):
    params = {"BusStopCode": "54321"}
    cached_payload = {"value": [{"ServiceNo": "42"}]}
    cache_key = CacheClient.build_cache_key("/v3/BusArrival", params)
    cache_client = StubCacheClient(initial={cache_key: cached_payload})
    lta_client = StubLTAClient(payload={"value": [{"ServiceNo": "10"}]})
    _override_clients(app, lta_client, cache_client)

    response = client.get("/api/v1/bus-arrival", params=params)

    assert response.status_code == 200
    assert response.json() == cached_payload
    assert lta_client.calls == []
    assert cache_client.set_calls == []


def test_bus_services_maps_upstream_http_error(app, client):
    request = httpx.Request("GET", "https://example.test/BusServices")
    response = httpx.Response(503, request=request, text="service unavailable")
    upstream_error = httpx.HTTPStatusError("upstream failure", request=request, response=response)

    lta_client = StubLTAClient(error=upstream_error)
    cache_client = StubCacheClient()
    _override_clients(app, lta_client, cache_client)

    api_response = client.get("/api/v1/bus-services", params={"$skip": 10})

    assert api_response.status_code == 503
    assert api_response.json()["detail"]["message"] == "Upstream DataMall request failed"
    assert api_response.json()["detail"]["upstream_status"] == 503
    assert api_response.json()["detail"]["upstream_body"] == "service unavailable"
