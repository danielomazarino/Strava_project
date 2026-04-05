from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from uuid import uuid4

from app.core.config import Settings
from app.core.security import encrypt_secret
from app.services.oauth_service import OAuthTokenSet
from app.workers.sync_worker import SyncWorker


@dataclass
class FakeUser:
    id: object
    strava_athlete_id: int
    access_token_encrypted: str
    refresh_token_encrypted: str
    token_expires_at: datetime


class FakeUserRepository:
    def __init__(self, users: list[FakeUser]):
        self.users = users
        self.upsert_calls: list[dict] = []

    def list_all_users(self):
        return self.users

    def get_by_strava_athlete_id(self, strava_athlete_id: int):
        for user in self.users:
            if user.strava_athlete_id == strava_athlete_id:
                return user
        return None

    def upsert_tokens(self, **kwargs):
        self.upsert_calls.append(kwargs)
        user = self.get_by_strava_athlete_id(kwargs["strava_athlete_id"])
        if user is not None:
            user.access_token_encrypted = encrypt_secret(kwargs["access_token"], kwargs["secret_key"])
            user.refresh_token_encrypted = encrypt_secret(kwargs["refresh_token"], kwargs["secret_key"])
            user.token_expires_at = kwargs["token_expires_at"]
        return user


class FakeActivityRepository:
    def __init__(self, latest_dates: dict[object, datetime | None]):
        self.latest_dates = latest_dates
        self.calls: list[object] = []

    def get_latest_start_date_for_user(self, *, user_id):
        self.calls.append(user_id)
        return self.latest_dates[user_id]


class FakeOAuthService:
    def __init__(self):
        self.calls: list[str] = []

    def refresh_tokens(self, *, refresh_token: str):
        self.calls.append(refresh_token)
        return OAuthTokenSet(
            strava_athlete_id=123,
            access_token="refreshed-access-token",
            refresh_token="refreshed-refresh-token",
            expires_at=datetime(2026, 4, 30, 0, 0, tzinfo=timezone.utc),
        )


class FakeImportService:
    def __init__(self):
        self.calls: list[dict] = []

    def import_activities(self, *, strava_athlete_id: int, after=None, before=None):
        self.calls.append({"strava_athlete_id": strava_athlete_id, "after": after, "before": before})
        return 4


def test_sync_worker_refreshes_expired_tokens_and_syncs_incrementally():
    secret_key = "unit-test-secret"
    expired_user = FakeUser(
        id=uuid4(),
        strava_athlete_id=123,
        access_token_encrypted=encrypt_secret("expired-access-token", secret_key),
        refresh_token_encrypted=encrypt_secret("expired-refresh-token", secret_key),
        token_expires_at=datetime(2026, 4, 5, 0, 0, tzinfo=timezone.utc),
    )
    fresh_user = FakeUser(
        id=uuid4(),
        strava_athlete_id=456,
        access_token_encrypted=encrypt_secret("fresh-access-token", secret_key),
        refresh_token_encrypted=encrypt_secret("fresh-refresh-token", secret_key),
        token_expires_at=datetime(2026, 4, 5, 2, 0, tzinfo=timezone.utc),
    )
    user_repository = FakeUserRepository([expired_user, fresh_user])
    activity_repository = FakeActivityRepository(
        {
            expired_user.id: datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc),
            fresh_user.id: None,
        }
    )
    oauth_service = FakeOAuthService()
    import_service = FakeImportService()
    worker = SyncWorker(
        settings=Settings(secret_key=secret_key),
        user_repository=user_repository,
        activity_repository=activity_repository,
        oauth_service=oauth_service,
        import_service=import_service,
        now_provider=lambda: datetime(2026, 4, 5, 0, 30, tzinfo=timezone.utc),
        refresh_threshold_seconds=300,
    )

    results = worker.run_once()

    assert len(results) == 2
    assert results[0].strava_athlete_id == 123
    assert results[0].refreshed is True
    assert results[0].after == int(datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc).timestamp())
    assert import_service.calls[0] == {
        "strava_athlete_id": 123,
        "after": int(datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc).timestamp()),
        "before": None,
    }
    assert results[1].strava_athlete_id == 456
    assert results[1].refreshed is False
    assert results[1].after is None
    assert oauth_service.calls == ["expired-refresh-token"]
    assert len(user_repository.upsert_calls) == 1


def test_sync_worker_continues_when_a_user_fails():
    secret_key = "unit-test-secret"
    good_user = FakeUser(
        id=uuid4(),
        strava_athlete_id=123,
        access_token_encrypted=encrypt_secret("good-access-token", secret_key),
        refresh_token_encrypted=encrypt_secret("good-refresh-token", secret_key),
        token_expires_at=datetime(2026, 4, 6, 0, 0, tzinfo=timezone.utc),
    )
    failing_user = FakeUser(
        id=uuid4(),
        strava_athlete_id=999,
        access_token_encrypted=encrypt_secret("bad-access-token", secret_key),
        refresh_token_encrypted=encrypt_secret("bad-refresh-token", secret_key),
        token_expires_at=datetime(2026, 4, 6, 0, 0, tzinfo=timezone.utc),
    )

    class FailingImportService(FakeImportService):
        def import_activities(self, *, strava_athlete_id: int, after=None, before=None):
            if strava_athlete_id == 999:
                raise RuntimeError("boom")
            return super().import_activities(strava_athlete_id=strava_athlete_id, after=after, before=before)

    user_repository = FakeUserRepository([good_user, failing_user])
    activity_repository = FakeActivityRepository({good_user.id: None, failing_user.id: None})
    worker = SyncWorker(
        settings=Settings(secret_key=secret_key),
        user_repository=user_repository,
        activity_repository=activity_repository,
        oauth_service=FakeOAuthService(),
        import_service=FailingImportService(),
        now_provider=lambda: datetime(2026, 4, 5, 0, 30, tzinfo=timezone.utc),
    )

    results = worker.run_once()

    assert results[0].error is None
    assert results[1].error == "boom"
