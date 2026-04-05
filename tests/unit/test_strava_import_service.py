from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.core.config import Settings
from app.core.security import encrypt_secret
from app.services.strava_import_service import StravaImportService


@dataclass
class FakeResponse:
    payload: object

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = responses
        self.requests: list[tuple[str, dict, dict | None]] = []

    def get(self, url: str, headers: dict, params: dict | None = None):
        self.requests.append((url, headers, params))
        return self.responses.pop(0)


class FakeUserRepository:
    def __init__(self, secret_key: str):
        self.user = SimpleNamespace(
            id=uuid4(),
            strava_athlete_id=123,
            access_token_encrypted=encrypt_secret("access-token", secret_key),
        )

    def get_by_strava_athlete_id(self, strava_athlete_id: int):
        if strava_athlete_id == self.user.strava_athlete_id:
            return self.user
        return None


class FakeActivityRepository:
    def __init__(self):
        self.calls: list[dict] = []

    def upsert_activity(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(id=uuid4(), strava_activity_id=kwargs["strava_activity_id"])


def test_import_activities_pages_through_summaries_and_fetches_details():
    settings = Settings(secret_key="unit-test-secret")
    http_client = FakeHttpClient(
        [
            FakeResponse([
                {"id": 111},
                {"id": 222},
            ]),
            FakeResponse({
                "id": 111,
                "name": "Run One",
                "type": "Run",
                "start_date": "2026-04-05T08:00:00Z",
                "distance": 10000,
                "moving_time": 3600,
                "elapsed_time": 3650,
                "total_elevation_gain": 120,
                "description": "Morning session",
                "map": {"summary_polyline": "polyline-1"},
                "timezone": "UTC",
                "location_country": "GB",
            }),
            FakeResponse({
                "id": 222,
                "name": "Run Two",
                "type": "Run",
                "start_date": "2026-04-06T08:00:00Z",
                "distance": 12000,
                "moving_time": 4000,
                "elapsed_time": 4050,
                "total_elevation_gain": 150,
                "description": "Long session",
                "map": {"summary_polyline": "polyline-2"},
                "timezone": "UTC",
                "location_country": "GB",
            }),
            FakeResponse([]),
        ]
    )
    user_repository = FakeUserRepository("unit-test-secret")
    activity_repository = FakeActivityRepository()
    service = StravaImportService(
        settings=settings,
        user_repository=user_repository,
        activity_repository=activity_repository,
        http_client=http_client,
    )

    imported_count = service.import_activities(strava_athlete_id=123, after=10, before=20)

    assert imported_count == 2
    assert http_client.requests[0][0] == "https://www.strava.com/api/v3/athlete/activities"
    assert http_client.requests[0][2] == {"page": 1, "per_page": 200, "after": 10, "before": 20}
    assert http_client.requests[1][0] == "https://www.strava.com/api/v3/activities/111"
    assert http_client.requests[2][0] == "https://www.strava.com/api/v3/activities/222"
    assert activity_repository.calls[0]["strava_activity_id"] == 111
    assert activity_repository.calls[0]["start_date"] == datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc)
    assert activity_repository.calls[1]["polyline"] == "polyline-2"