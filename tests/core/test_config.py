from app.core.config import Settings


def test_settings_default_backend_port_is_8000():
    settings = Settings(datamall_api_key="test-account-key")

    assert settings.app_port == 8000


def test_settings_reads_backend_port_from_env_value():
    settings = Settings(datamall_api_key="test-account-key", app_port=9010)

    assert settings.app_port == 9010