from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings


class LTAClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def startup(self) -> None:
        limits = httpx.Limits(
            max_connections=self._settings.max_connections,
            max_keepalive_connections=self._settings.max_keepalive_connections,
        )
        timeout = httpx.Timeout(self._settings.request_timeout_seconds)
        self._client = httpx.AsyncClient(
            base_url=self._settings.datamall_base_url,
            headers={
                "AccountKey": self._settings.datamall_api_key,
                "accept": "application/json",
            },
            timeout=timeout,
            limits=limits,
        )

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("LTA client not initialized")

        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()
