import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_get_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("SECRET_KEY", "secret-key")
    monkeypatch.setenv("LLM_MODEL_PATH", "/models/gemma")
    monkeypatch.setenv("APP_ENV", "test")

    settings = get_settings()

    assert settings.strava_client_id == "client-id"
    assert settings.strava_client_secret == "client-secret"
    assert settings.database_url == "postgresql://example"
    assert settings.secret_key == "secret-key"
    assert settings.llm_model_path == "/models/gemma"
    assert settings.environment == "test"


def test_get_settings_uses_dev_fallbacks(monkeypatch):
    monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
    monkeypatch.delenv("STRAVA_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("APP_ENV", "development")

    settings = get_settings()

    assert settings.secret_key == "strava-training-diary-dev-secret"
    assert settings.enable_dev_mock_auth is True


def test_get_settings_rejects_sqlite_in_production(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///production.sqlite3")
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("SECRET_KEY", "secret-key")
    monkeypatch.setenv("LLM_MODEL_PATH", "/models/gemma")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")

    with pytest.raises(ValueError, match="Railway deployments must use PostgreSQL"):
        get_settings()


def test_get_settings_rejects_missing_production_values(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")

    with pytest.raises(ValueError, match="Missing required production settings"):
        get_settings()


def test_get_settings_rejects_dev_mock_auth_in_production(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("SECRET_KEY", "secret-key")
    monkeypatch.setenv("LLM_MODEL_PATH", "/models/gemma")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
    monkeypatch.setenv("ENABLE_DEV_MOCK_AUTH", "true")

    with pytest.raises(ValueError, match="ENABLE_DEV_MOCK_AUTH must remain false in production"):
        get_settings()


def test_app_env_development_overrides_railway_production(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")

    settings = get_settings()

    assert settings.environment == "development"
    assert settings.database_url.startswith("sqlite:///")
    assert settings.enable_dev_mock_auth is True