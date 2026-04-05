from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Protocol

from app.core.config import Settings
from app.core.security import decrypt_secret


class UserRecord(Protocol):
    id: Any
    strava_athlete_id: int
    refresh_token_encrypted: str
    token_expires_at: datetime


class UserRepositoryLike(Protocol):
    def list_all_users(self) -> list[UserRecord]:
        ...

    def get_by_strava_athlete_id(self, strava_athlete_id: int) -> UserRecord | None:
        ...

    def upsert_tokens(
        self,
        *,
        strava_athlete_id: int,
        access_token: str,
        refresh_token: str,
        token_expires_at: datetime,
        secret_key: str,
    ) -> UserRecord:
        ...


class ActivityRepositoryLike(Protocol):
    def get_latest_start_date_for_user(self, *, user_id: Any) -> datetime | None:
        ...


class OAuthServiceLike(Protocol):
    def refresh_tokens(self, *, refresh_token: str):
        ...


class StravaImportServiceLike(Protocol):
    def import_activities(self, *, strava_athlete_id: int, after=None, before=None) -> int:
        ...


@dataclass(frozen=True)
class SyncResult:
    strava_athlete_id: int
    refreshed: bool
    imported_count: int
    after: int | None
    error: str | None = None


@dataclass
class SyncWorker:
    settings: Settings
    user_repository: UserRepositoryLike
    activity_repository: ActivityRepositoryLike
    oauth_service: OAuthServiceLike
    import_service: StravaImportServiceLike
    now_provider: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    refresh_threshold_seconds: int = 300

    def run_once(self) -> list[SyncResult]:
        results: list[SyncResult] = []
        for user in self.user_repository.list_all_users():
            try:
                refreshed = False
                if self._needs_refresh(user.token_expires_at):
                    refreshed = self._refresh_user_tokens(user.strava_athlete_id)

                latest_start_date = self.activity_repository.get_latest_start_date_for_user(user_id=user.id)
                after = int(latest_start_date.timestamp()) if latest_start_date is not None else None
                imported_count = self.import_service.import_activities(
                    strava_athlete_id=user.strava_athlete_id,
                    after=after,
                )
                results.append(
                    SyncResult(
                        strava_athlete_id=user.strava_athlete_id,
                        refreshed=refreshed,
                        imported_count=imported_count,
                        after=after,
                    )
                )
            except Exception as exc:  # pragma: no cover - background safety net
                results.append(
                    SyncResult(
                        strava_athlete_id=user.strava_athlete_id,
                        refreshed=False,
                        imported_count=0,
                        after=None,
                        error=str(exc),
                    )
                )
        return results

    def run_forever(self, *, interval_seconds: int = 300) -> None:
        while True:
            self.run_once()
            self._sleep(interval_seconds)

    def _refresh_user_tokens(self, strava_athlete_id: int) -> bool:
        user = self.user_repository.get_by_strava_athlete_id(strava_athlete_id)
        if user is None:
            return False

        refresh_token = decrypt_secret(user.refresh_token_encrypted, self.settings.secret_key)
        token_set = self.oauth_service.refresh_tokens(refresh_token=refresh_token)
        self.user_repository.upsert_tokens(
            strava_athlete_id=token_set.strava_athlete_id,
            access_token=token_set.access_token,
            refresh_token=token_set.refresh_token,
            token_expires_at=token_set.expires_at,
            secret_key=self.settings.secret_key,
        )
        return True

    def _needs_refresh(self, token_expires_at: datetime) -> bool:
        return token_expires_at <= self.now_provider() + timedelta(seconds=self.refresh_threshold_seconds)

    @staticmethod
    def _sleep(interval_seconds: int) -> None:
        import time

        time.sleep(interval_seconds)
