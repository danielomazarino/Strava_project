from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.auth import get_oauth_service
from app.core.config import Settings, get_settings
from app.core.security import create_oauth_state
from app.main import app


class FakeOAuthService:
    def complete_callback(self, *, code: str, state: str, redirect_uri: str):
        return SimpleNamespace(id=uuid4(), strava_athlete_id=123456)


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


def test_callback_returns_connected_payload():
    app.dependency_overrides[get_oauth_service] = lambda: FakeOAuthService()
    client = TestClient(app)
    state = create_oauth_state("unit-test-secret")

    response = client.get(f"/auth/callback?code=oauth-code&state={state}")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "connected"
    assert response.json()["strava_athlete_id"] == 123456


def test_callback_rejects_missing_parameters():
    app.dependency_overrides[get_oauth_service] = lambda: FakeOAuthService()
    client = TestClient(app)

    response = client.get("/auth/callback")

    app.dependency_overrides.clear()

    assert response.status_code == 400