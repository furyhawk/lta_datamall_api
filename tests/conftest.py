import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.main import create_app

os.environ.setdefault("DATAMALL_API_KEY", "test-account-key")
os.environ.setdefault("VALKEY_ENABLED", "false")


@pytest.fixture
def app() -> FastAPI:
    get_settings.cache_clear()
    return create_app()


@pytest.fixture
def client(app: FastAPI):
    with TestClient(app) as test_client:
        yield test_client
