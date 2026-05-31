from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import bus, health
from app.core.config import get_settings
from app.services.cache import CacheClient
from app.services.lta_client import LTAClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    lta_client = LTAClient(settings)
    cache_client = CacheClient(settings)
    await lta_client.startup()
    await cache_client.startup()
    app.state.lta_client = lta_client
    app.state.cache_client = cache_client
    yield
    await lta_client.shutdown()
    await cache_client.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.include_router(health.router)
    app.include_router(bus.router)

    return app


app = create_app()
