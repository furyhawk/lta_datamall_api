from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.services.cache import CacheClient
from app.services.lta_client import LTAClient

router = APIRouter(prefix="/api/v1", tags=["Bus"])


async def get_lta_client(request: Request) -> LTAClient:
    return request.app.state.lta_client


async def get_cache_client(request: Request) -> CacheClient:
    return request.app.state.cache_client


def _map_httpx_error(err: httpx.HTTPStatusError) -> HTTPException:
    return HTTPException(
        status_code=err.response.status_code,
        detail={
            "message": "Upstream DataMall request failed",
            "upstream_status": err.response.status_code,
            "upstream_body": err.response.text,
        },
    )


async def _fetch_with_cache(
    path: str,
    params: dict[str, Any],
    client: LTAClient,
    cache: CacheClient,
    ttl_seconds: int,
) -> dict[str, Any]:
    cache_key = cache.build_cache_key(path, params)
    cached = await cache.get_json(cache_key)
    if cached is not None:
        return cached

    payload = await client.get(path, params=params)
    await cache.set_json(cache_key, payload, ttl_seconds=ttl_seconds)
    return payload


@router.get("/bus-arrival")
async def bus_arrival(
    bus_stop_code: str = Query(..., alias="BusStopCode", min_length=5, max_length=5),
    service_no: str | None = Query(None, alias="ServiceNo"),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {"BusStopCode": bus_stop_code}
    if service_no:
        params["ServiceNo"] = service_no
    try:
        return await _fetch_with_cache("/v3/BusArrival", params, client, cache, ttl_seconds=15)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err


@router.get("/bus-services")
async def bus_services(
    service_no: str | None = Query(None, alias="ServiceNo"),
    skip: int | None = Query(None, alias="$skip", ge=0),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if service_no:
        params["ServiceNo"] = service_no
    if skip is not None:
        params["$skip"] = skip
    try:
        return await _fetch_with_cache("/BusServices", params, client, cache, ttl_seconds=300)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err


@router.get("/bus-routes")
async def bus_routes(
    skip: int | None = Query(None, alias="$skip", ge=0),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if skip is not None:
        params["$skip"] = skip
    try:
        return await _fetch_with_cache("/BusRoutes", params, client, cache, ttl_seconds=300)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err


@router.get("/bus-stops")
async def bus_stops(
    bus_stop_code: str | None = Query(None, alias="BusStopCode", min_length=5, max_length=5),
    skip: int | None = Query(None, alias="$skip", ge=0),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if bus_stop_code:
        params["BusStopCode"] = bus_stop_code
    if skip is not None:
        params["$skip"] = skip
    try:
        return await _fetch_with_cache("/BusStops", params, client, cache, ttl_seconds=1800)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err


@router.get("/passenger-volume/bus")
async def passenger_volume_bus(
    date: str | None = Query(None, alias="Date", pattern=r"^[0-9]{6}$"),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if date:
        params["Date"] = date
    try:
        return await _fetch_with_cache("/PV/Bus", params, client, cache, ttl_seconds=21600)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err


@router.get("/passenger-volume/od-bus")
async def passenger_volume_od_bus(
    date: str | None = Query(None, alias="Date", pattern=r"^[0-9]{6}$"),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if date:
        params["Date"] = date
    try:
        return await _fetch_with_cache("/PV/ODBus", params, client, cache, ttl_seconds=21600)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err


@router.get("/planned-bus-routes")
async def planned_bus_routes(
    skip: int | None = Query(None, alias="$skip", ge=0),
    client: LTAClient = Depends(get_lta_client),
    cache: CacheClient = Depends(get_cache_client),
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if skip is not None:
        params["$skip"] = skip
    try:
        return await _fetch_with_cache("/PlannedBusRoutes", params, client, cache, ttl_seconds=900)
    except httpx.HTTPStatusError as err:
        raise _map_httpx_error(err) from err
