from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.auth import get_activity_repository, get_oauth_service, get_strava_import_service, mock_login
from app.core.config import Settings, get_settings
from app.core.security import create_oauth_state
from app.db.bootstrap import DEV_DEMO_STRAVA_ATHLETE_ID
from app.main import app


class FakeOAuthService:
    def complete_callback(self, *, code: str, state: str, redirect_uri: str):
        return SimpleNamespace(id=uuid4(), strava_athlete_id=123456)


class RecordingOAuthService:
    def __init__(self):
        self.redirect_uris: list[str] = []

    def complete_callback(self, *, code: str, state: str, redirect_uri: str):
        self.redirect_uris.append(redirect_uri)
        return SimpleNamespace(id=uuid4(), strava_athlete_id=123456)


class FakeActivityRepository:
    def __init__(self, latest_start_date: datetime | None):
        self.latest_start_date = latest_start_date
        self.calls: list[object] = []

    def get_latest_start_date_for_user(self, *, user_id):
        self.calls.append(user_id)
        return self.latest_start_date


class FakeImportService:
    def __init__(self):
        self.calls: list[dict] = []

    def import_activities(self, *, strava_athlete_id: int, after=None, before=None):
        self.calls.append({"strava_athlete_id": strava_athlete_id, "after": after, "before": before})
        return 17


def _override_callback_dependencies(activity_repository: FakeActivityRepository | None = None, import_service: FakeImportService | None = None):
    app.dependency_overrides[get_oauth_service] = lambda: FakeOAuthService()
    app.dependency_overrides[get_activity_repository] = lambda: activity_repository or FakeActivityRepository(None)
    app.dependency_overrides[get_strava_import_service] = lambda: import_service or FakeImportService()


def test_login_redirects_to_strava_authorize_url(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret-456")
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret")

    client = TestClient(app)

    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"].startswith("https://www.strava.com/oauth/authorize?")
    assert "client_id=client-123" in response.headers["location"]
    assert "response_type=code" in response.headers["location"]


def test_login_uses_https_redirect_uri_in_production(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret-456")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("LLM_MODEL_PATH", "/models/gemma")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")

    client = TestClient(app)

    response = client.get("/auth/login", follow_redirects=False)

    assert response.status_code == 302
    assert "redirect_uri=https%3A%2F%2Ftestserver%2Fauth%2Fcallback" in response.headers["location"]


def test_login_falls_back_to_mock_auth_without_client_id(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
    monkeypatch.delenv("STRAVA_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("APP_ENV", "development")

    client = TestClient(app)

    response = client.get(
        "/auth/login",
        headers={"referer": "http://127.0.0.1:5173/auth/login"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"].startswith("http://testserver/auth/mock-login?")
    assert "return_to=http%3A%2F%2F127.0.0.1%3A5173%2Fauth%2Fcallback" in response.headers["location"]


def test_mock_login_uses_demo_athlete_id(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("STRAVA_CLIENT_ID", raising=False)
    monkeypatch.delenv("STRAVA_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("APP_ENV", "development")

    client = TestClient(app)

    response = client.get(
        "/auth/mock-login?return_to=http%3A%2F%2F127.0.0.1%3A5173%2Fauth%2Fcallback",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert f"code=mock-{DEV_DEMO_STRAVA_ATHLETE_ID}" in response.headers["location"]


def test_mock_login_is_disabled_in_production():
    settings = Settings(
        strava_client_id="client-id",
        strava_client_secret="secret",
        database_url="postgresql://example",
        secret_key="unit-test-secret",
        llm_model_path="/models/gemma",
        cors_origins="https://example.com",
        log_level="INFO",
        environment="production",
        enable_dev_mock_auth=True,
    )

    with pytest.raises(HTTPException) as excinfo:
        mock_login(return_to="http://127.0.0.1:5173/auth/callback", settings=settings)

    assert excinfo.value.status_code == 404


def test_callback_returns_connected_payload():
    activity_repository = FakeActivityRepository(datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc))
    import_service = FakeImportService()
    _override_callback_dependencies(activity_repository, import_service)
    client = TestClient(app)
    state = create_oauth_state("unit-test-secret")

    response = client.get(f"/auth/callback?code=oauth-code&state={state}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "connected"
    assert response.json()["strava_athlete_id"] == 123456
    assert import_service.calls == [
        {"strava_athlete_id": 123456, "after": int(datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc).timestamp()), "before": None}
    ]


def test_callback_uses_https_redirect_uri_in_production(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-123")
    monkeypatch.setenv("STRAVA_CLIENT_SECRET", "secret-456")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("LLM_MODEL_PATH", "/models/gemma")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")

    oauth_service = RecordingOAuthService()
    activity_repository = FakeActivityRepository(None)
    import_service = FakeImportService()
    app.dependency_overrides[get_oauth_service] = lambda: oauth_service
    app.dependency_overrides[get_activity_repository] = lambda: activity_repository
    app.dependency_overrides[get_strava_import_service] = lambda: import_service

    client = TestClient(app)
    state = create_oauth_state("unit-test-secret")

    response = client.get(f"/auth/callback?code=oauth-code&state={state}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert oauth_service.redirect_uris == ["https://testserver/auth/callback"]


def test_callback_redirects_browser_navigation_to_frontend():
    _override_callback_dependencies(FakeActivityRepository(None), FakeImportService())
    client = TestClient(app)
    state = create_oauth_state("unit-test-secret", return_to="http://127.0.0.1:5173/auth/callback")

    response = client.get(
        f"/auth/callback?code=oauth-code&state={state}",
        headers={"accept": "text/html"},
        follow_redirects=False,
    )

    app.dependency_overrides.clear()

    assert response.status_code == 302
    assert response.headers["location"].startswith("http://127.0.0.1:5173/auth/callback?")
    assert "user_id=" in response.headers["location"]
    assert "strava_athlete_id=123456" in response.headers["location"]


def test_callback_rejects_missing_parameters():
    _override_callback_dependencies(FakeActivityRepository(None), FakeImportService())
    client = TestClient(app)

    response = client.get("/auth/callback")

    app.dependency_overrides.clear()

    assert response.status_code == 400