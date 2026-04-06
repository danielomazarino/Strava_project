from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.services.diary_service import DiaryService


@dataclass
class FakeActivity:
    id: object
    strava_activity_id: int
    name: str
    type: str
    start_date: datetime
    distance: float
    description: str
    location_country: str


class FakeActivityRepository:
    def list_by_user_id(self, *, user_id):
        return [
            FakeActivity(
                id=uuid4(),
                strava_activity_id=222,
                name="Second",
                type="Run",
                start_date=datetime(2026, 4, 6, 8, 0, tzinfo=timezone.utc),
                distance=12_000,
                description="Second entry",
                location_country="GB",
            ),
            FakeActivity(
                id=uuid4(),
                strava_activity_id=111,
                name="First",
                type="Ride",
                start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
                distance=50_000,
                description="First entry",
                location_country="FR",
            ),
        ]


@dataclass
class FakeUser:
    id: object
    strava_athlete_id: int


class FakeUserRepository:
    def get_by_strava_athlete_id(self, strava_athlete_id: int):
        if strava_athlete_id == 123:
            return FakeUser(id=uuid4(), strava_athlete_id=strava_athlete_id)
        return None


def test_diary_service_returns_entries_in_order():
    service = DiaryService(user_repository=FakeUserRepository(), activity_repository=FakeActivityRepository())

    entries = service.list_entries(strava_athlete_id=123)

    assert [entry.strava_activity_id for entry in entries] == [222, 111]
    assert entries[0].name == "Second"