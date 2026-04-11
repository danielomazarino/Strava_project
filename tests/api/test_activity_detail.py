from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.activities import get_activity_repository, get_user_repository
from app.main import app


class FakeUserRepository:
    def __init__(self, user):
        self.user = user

    def get_by_strava_athlete_id(self, strava_athlete_id: int):
        if self.user is not None and strava_athlete_id == self.user.strava_athlete_id:
            return self.user
        return None


class FakeActivityRepository:
    def __init__(self, activity):
        self.activity = activity

    def get_by_user_and_strava_activity_id(self, *, user_id, strava_activity_id: int):
        if self.activity is not None and strava_activity_id == self.activity.strava_activity_id:
            return self.activity
        return None


def test_activity_detail_endpoint_returns_activity_payload():
    user = SimpleNamespace(id=uuid4(), strava_athlete_id=123)
    activity = SimpleNamespace(
        id=uuid4(),
        strava_activity_id=456,
        name="Long Run",
        type="Run",
        start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
        distance=21000.5,
        moving_time=5400,
        elapsed_time=5500,
        elevation_gain=245.0,
        description="A steady long run.",
        polyline="encoded-polyline",
        timezone="UTC",
        location_country="GB",
    )

    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository(user)
    app.dependency_overrides[get_activity_repository] = lambda: FakeActivityRepository(activity)
    client = TestClient(app)

    response = client.get("/activities/456?strava_athlete_id=123")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["activity"]["strava_activity_id"] == 456
    assert response.json()["activity"]["polyline"] == "encoded-polyline"