from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import valkey.asyncio as valkey
from valkey.exceptions import ValkeyError

from app.core.config import Settings

logger = logging.getLogger(__name__)


class CacheClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: valkey.Valkey | None = None

    async def startup(self) -> None:
        if not self._settings.valkey_enabled:
            return

        self._client = valkey.from_url(
            self._settings.valkey_url,
            decode_responses=True,
            socket_connect_timeout=self._settings.valkey_connect_timeout_seconds,
        )
        try:
            await self._client.ping()
        except ValkeyError:
            logger.exception("Valkey ping failed; continuing without cache")
            await self.shutdown()

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_json(self, key: str) -> dict[str, Any] | None:
        if self._client is None:
            return None

        try:
            value = await self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (ValkeyError, json.JSONDecodeError):
            logger.exception("Valkey get failed for key=%s", key)
            return None

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int | None = None) -> None:
        if self._client is None:
            return

        ttl = ttl_seconds or self._settings.valkey_default_ttl_seconds
        try:
            payload = json.dumps(value, separators=(",", ":"), ensure_ascii=True)
            await self._client.set(key, payload, ex=ttl)
        except ValkeyError:
            logger.exception("Valkey set failed for key=%s", key)

    @staticmethod
    def build_cache_key(path: str, params: dict[str, Any] | None = None) -> str:
        canonical = json.dumps(params or {}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        digest = hashlib.sha1(f"{path}?{canonical}".encode("utf-8")).hexdigest()
        return f"lta:{path}:{digest}"
