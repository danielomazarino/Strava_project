from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from datetime import timedelta
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.core.config import Settings
from app.core.security import verify_oauth_state
from app.db.repositories.user_repo import UserRepository


@dataclass(frozen=True)
class OAuthTokenSet:
    strava_athlete_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime


def build_authorize_url(
    *,
    client_id: str,
    redirect_uri: str,
    state: str,
    scope: str = "activity:read_all",
    authorize_url: str = "https://www.strava.com/oauth/authorize",
) -> str:
    if not client_id:
        raise HTTPException(status_code=500, detail="STRAVA_CLIENT_ID is not configured")

    query = urlencode(
        [
            ("client_id", client_id),
            ("redirect_uri", redirect_uri),
            ("response_type", "code"),
            ("scope", scope),
            ("state", state),
        ]
    )
    return f"{authorize_url}?{query}"


class OAuthService:
    def __init__(
        self,
        *,
        settings: Settings,
        user_repository: UserRepository,
        http_client: httpx.Client,
        token_url: str = "https://www.strava.com/oauth/token",
    ):
        self.settings = settings
        self.user_repository = user_repository
        self.http_client = http_client
        self.token_url = token_url

    def exchange_code_for_tokens(
        self,
        *,
        code: str,
        redirect_uri: str,
    ) -> OAuthTokenSet:
        response = self.http_client.post(
            self.token_url,
            data={
                "client_id": self.settings.strava_client_id,
                "client_secret": self.settings.strava_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        response.raise_for_status()
        return self._parse_token_response(response.json())

    def refresh_tokens(self, *, refresh_token: str) -> OAuthTokenSet:
        response = self.http_client.post(
            self.token_url,
            data={
                "client_id": self.settings.strava_client_id,
                "client_secret": self.settings.strava_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        return self._parse_token_response(response.json())

    def complete_callback(
        self,
        *,
        code: str,
        state: str,
        redirect_uri: str,
    ):
        if not verify_oauth_state(state, self.settings.secret_key):
            raise HTTPException(status_code=400, detail="Invalid OAuth state")

        if code.startswith("mock-") and self.settings.enable_dev_mock_auth:
            strava_athlete_id_raw = code.removeprefix("mock-")
            strava_athlete_id = int(strava_athlete_id_raw)
            expires_at = datetime.now(timezone.utc) + timedelta(days=90)
            return self.user_repository.upsert_tokens(
                strava_athlete_id=strava_athlete_id,
                access_token=f"mock-access-token-{strava_athlete_id}",
                refresh_token=f"mock-refresh-token-{strava_athlete_id}",
                token_expires_at=expires_at,
                secret_key=self.settings.secret_key,
            )

        token_set = self.exchange_code_for_tokens(code=code, redirect_uri=redirect_uri)
        return self.user_repository.upsert_tokens(
            strava_athlete_id=token_set.strava_athlete_id,
            access_token=token_set.access_token,
            refresh_token=token_set.refresh_token,
            token_expires_at=token_set.expires_at,
            secret_key=self.settings.secret_key,
        )

    @staticmethod
    def _parse_token_response(data: dict[str, Any]) -> OAuthTokenSet:
        try:
            athlete = data["athlete"]
            strava_athlete_id = int(athlete["id"])
            access_token = str(data["access_token"])
            refresh_token = str(data["refresh_token"])
            expires_at = datetime.fromtimestamp(int(data["expires_at"]), tz=timezone.utc)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid Strava token response") from exc

        return OAuthTokenSet(
            strava_athlete_id=strava_athlete_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )