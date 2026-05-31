import asyncio
import json

from valkey.exceptions import ValkeyError

from app.core.config import Settings
from app.services.cache import CacheClient


def make_settings(**overrides):
    return Settings(datamall_api_key="test-account-key", **overrides)


def run(coro):
    return asyncio.run(coro)


class FakeValkeyClient:
    def __init__(self, get_value=None, get_error=None, set_error=None):
        self.get_value = get_value
        self.get_error = get_error
        self.set_error = set_error
        self.get_calls = []
        self.set_calls = []
        self.ping_calls = 0
        self.closed = False

    async def ping(self):
        self.ping_calls += 1

    async def get(self, key):
        self.get_calls.append(key)
        if self.get_error is not None:
            raise self.get_error
        return self.get_value

    async def set(self, key, value, ex=None):
        self.set_calls.append((key, value, ex))
        if self.set_error is not None:
            raise self.set_error

    async def aclose(self):
        self.closed = True


def test_build_cache_key_is_deterministic():
    first = CacheClient.build_cache_key("/v3/BusArrival", {"BusStopCode": "12345", "ServiceNo": "10"})
    second = CacheClient.build_cache_key("/v3/BusArrival", {"ServiceNo": "10", "BusStopCode": "12345"})

    assert first == second


def test_get_json_returns_parsed_payload():
    cache = CacheClient(make_settings(valkey_enabled=True))
    cache._client = FakeValkeyClient(get_value=json.dumps({"value": [1, 2, 3]}))

    result = run(cache.get_json("lta:/v3/BusArrival:test"))

    assert result == {"value": [1, 2, 3]}


def test_get_json_returns_none_for_invalid_payload():
    cache = CacheClient(make_settings(valkey_enabled=True))
    cache._client = FakeValkeyClient(get_value="not-json")

    result = run(cache.get_json("lta:/v3/BusArrival:test"))

    assert result is None


def test_get_json_returns_none_when_cache_is_unavailable():
    cache = CacheClient(make_settings(valkey_enabled=True))
    cache._client = FakeValkeyClient(get_error=ValkeyError("boom"))

    result = run(cache.get_json("lta:/v3/BusArrival:test"))

    assert result is None


def test_set_json_uses_default_ttl_when_not_provided():
    cache = CacheClient(make_settings(valkey_default_ttl_seconds=321))
    cache._client = FakeValkeyClient()

    run(cache.set_json("lta:/v3/BusArrival:test", {"value": True}))

    assert cache._client.set_calls == [("lta:/v3/BusArrival:test", '{"value":true}', 321)]


def test_set_json_uses_explicit_ttl():
    cache = CacheClient(make_settings(valkey_default_ttl_seconds=321))
    cache._client = FakeValkeyClient()

    run(cache.set_json("lta:/v3/BusArrival:test", {"value": True}, ttl_seconds=12))

    assert cache._client.set_calls == [("lta:/v3/BusArrival:test", '{"value":true}', 12)]


def test_startup_disables_cache_when_ping_fails(monkeypatch):
    fake_client = FakeValkeyClient()

    class FakeFactory:
        def __init__(self):
            self.calls = []

        def __call__(self, url, decode_responses, socket_connect_timeout):
            self.calls.append((url, decode_responses, socket_connect_timeout))
            return fake_client

    factory = FakeFactory()

    async def failing_ping():
        raise ValkeyError("boom")

    fake_client.ping = failing_ping
    monkeypatch.setattr("app.services.cache.valkey.from_url", factory)

    cache = CacheClient(make_settings(valkey_enabled=True))
    run(cache.startup())

    assert factory.calls == [("redis://valkey:6379/0", True, 1.0)]
    assert fake_client.closed is True
    assert cache._client is None