import asyncio

import httpx

from app.core.config import Settings
from app.services import lta_client as lta_client_module
from app.services.lta_client import LTAClient


def make_settings(**overrides):
    return Settings(datamall_api_key="test-account-key", **overrides)


def run(coro):
    return asyncio.run(coro)


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload if payload is not None else {"value": []}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.test")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("boom", request=request, response=response)

    def json(self):
        return self._payload


class FakeAsyncClient:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls = []
        self.closed = False
        FakeAsyncClient.instances.append(self)

    async def get(self, path, params=None):
        self.calls.append((path, params))
        return FakeResponse({"path": path, "params": params})

    async def aclose(self):
        self.closed = True


def test_startup_configures_httpx_client(monkeypatch):
    FakeAsyncClient.instances = []
    monkeypatch.setattr(lta_client_module.httpx, "AsyncClient", FakeAsyncClient)

    client = LTAClient(make_settings(request_timeout_seconds=7.5, max_connections=12, max_keepalive_connections=6))
    run(client.startup())

    created = FakeAsyncClient.instances[0]
    assert created.kwargs["base_url"] == "https://datamall2.mytransport.sg/ltaodataservice"
    assert created.kwargs["headers"] == {"AccountKey": "test-account-key", "accept": "application/json"}
    assert created.kwargs["timeout"].connect == 7.5
    assert created.kwargs["timeout"].read == 7.5
    assert created.kwargs["timeout"].write == 7.5
    assert created.kwargs["timeout"].pool == 7.5
    assert created.kwargs["limits"].max_connections == 12
    assert created.kwargs["limits"].max_keepalive_connections == 6


def test_get_raises_before_startup():
    client = LTAClient(make_settings())

    try:
        run(client.get("/v3/BusArrival"))
        raised = False
    except RuntimeError as err:
        raised = True
        assert str(err) == "LTA client not initialized"

    assert raised is True


def test_get_returns_json_payload(monkeypatch):
    FakeAsyncClient.instances = []
    monkeypatch.setattr(lta_client_module.httpx, "AsyncClient", FakeAsyncClient)

    client = LTAClient(make_settings())
    run(client.startup())

    payload = run(client.get("/v3/BusArrival", params={"BusStopCode": "12345"}))

    assert payload == {"path": "/v3/BusArrival", "params": {"BusStopCode": "12345"}}
    assert FakeAsyncClient.instances[0].calls == [("/v3/BusArrival", {"BusStopCode": "12345"})]


def test_shutdown_closes_client(monkeypatch):
    FakeAsyncClient.instances = []
    monkeypatch.setattr(lta_client_module.httpx, "AsyncClient", FakeAsyncClient)

    client = LTAClient(make_settings())
    run(client.startup())
    created = FakeAsyncClient.instances[0]

    run(client.shutdown())

    assert created.closed is True