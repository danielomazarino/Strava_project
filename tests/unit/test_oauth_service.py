from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.core.config import Settings
from app.core.security import create_oauth_state
from app.services.oauth_service import OAuthService, build_authorize_url


@dataclass
class FakeResponse:
    payload: dict

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeHttpClient:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = responses
        self.requests: list[tuple[str, dict]] = []

    def post(self, url: str, data: dict):
        self.requests.append((url, data))
        return self.responses.pop(0)


class FakeUserRepository:
    def __init__(self):
        self.calls: list[dict] = []

    def upsert_tokens(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(id=uuid4(), strava_athlete_id=kwargs["strava_athlete_id"])


def test_build_authorize_url_includes_oauth_parameters():
    url = build_authorize_url(
        client_id="client-123",
        redirect_uri="https://example.test/auth/callback",
        state="state-token",
    )

    assert url == (
        "https://www.strava.com/oauth/authorize?"
        "client_id=client-123&"
        "redirect_uri=https%3A%2F%2Fexample.test%2Fauth%2Fcallback&"
        "response_type=code&"
        "scope=activity%3Aread_all&"
        "state=state-token"
    )


def test_complete_callback_persists_encrypted_tokens():
    settings = Settings(
        strava_client_id="client-123",
        strava_client_secret="secret-456",
        secret_key="unit-test-secret",
    )
    token_payload = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_at": 1_700_000_000,
        "athlete": {"id": 987654},
    }
    http_client = FakeHttpClient([FakeResponse(token_payload)])
    repository = FakeUserRepository()
    service = OAuthService(
        settings=settings,
        user_repository=repository,
        http_client=http_client,
    )
    state = create_oauth_state("unit-test-secret")

    user = service.complete_callback(
        code="oauth-code",
        state=state,
        redirect_uri="https://example.test/auth/callback",
    )

    assert user.strava_athlete_id == 987654
    assert http_client.requests[0][0] == "https://www.strava.com/oauth/token"
    assert http_client.requests[0][1]["grant_type"] == "authorization_code"
    assert repository.calls[0]["strava_athlete_id"] == 987654
    assert repository.calls[0]["access_token"] == "access-token"
    assert repository.calls[0]["refresh_token"] == "refresh-token"
    assert repository.calls[0]["token_expires_at"] == datetime.fromtimestamp(
        1_700_000_000,
        tz=timezone.utc,
    )
    assert repository.calls[0]["secret_key"] == "unit-test-secret"


def test_create_oauth_state_round_trips_return_to():
    from app.core.security import unpack_oauth_state

    state = create_oauth_state(
        "unit-test-secret",
        return_to="http://127.0.0.1:5173/auth/callback",
    )

    assert unpack_oauth_state(state, "unit-test-secret") == "http://127.0.0.1:5173/auth/callback"


def test_refresh_tokens_uses_refresh_grant():
    settings = Settings(
        strava_client_id="client-123",
        strava_client_secret="secret-456",
        secret_key="unit-test-secret",
    )
    token_payload = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "expires_at": 1_700_100_000,
        "athlete": {"id": 987654},
    }
    http_client = FakeHttpClient([FakeResponse(token_payload)])
    repository = FakeUserRepository()
    service = OAuthService(
        settings=settings,
        user_repository=repository,
        http_client=http_client,
    )

    token_set = service.refresh_tokens(refresh_token="refresh-token")

    assert token_set.access_token == "new-access-token"
    assert http_client.requests[0][1]["grant_type"] == "refresh_token"
    assert http_client.requests[0][1]["refresh_token"] == "refresh-token"