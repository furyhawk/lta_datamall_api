from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LTA DataMall Bus Backend"
    app_env: str = "development"
    app_debug: bool = False
    app_version: str = "0.1.0"

    datamall_base_url: str = "https://datamall2.mytransport.sg/ltaodataservice"
    datamall_api_key: str = Field(..., description="LTA DataMall AccountKey")

    request_timeout_seconds: float = 10.0
    max_connections: int = 200
    max_keepalive_connections: int = 100

    valkey_enabled: bool = True
    valkey_url: str = "redis://valkey:6379/0"
    valkey_connect_timeout_seconds: float = 1.0
    valkey_default_ttl_seconds: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
