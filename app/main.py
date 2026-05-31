from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import bus, health
from app.core.config import get_settings
from app.services.lta_client import LTAClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    client = LTAClient(settings)
    await client.startup()
    app.state.lta_client = client
    yield
    await client.shutdown()


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
