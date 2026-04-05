from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.services.search_service import SearchService


@dataclass
class FakeActivity:
    id: object
    strava_activity_id: int
    name: str
    type: str
    start_date: datetime
    description: str
    location_country: str


class FakeActivityRepository:
    def list_by_user_id(self, *, user_id):
        return [
            FakeActivity(
                id=uuid4(),
                strava_activity_id=1,
                name="Hill Repeats",
                type="Run",
                start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
                description="Workout in the UK hills",
                location_country="GB",
            ),
            FakeActivity(
                id=uuid4(),
                strava_activity_id=2,
                name="Easy Spin",
                type="Ride",
                start_date=datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc),
                description="Recovery ride",
                location_country="FR",
            ),
        ]

    def search_by_user_id(self, *, user_id, query: str):
        return [self.list_by_user_id(user_id=user_id)[0]] if query.lower() == "hills" else []


def test_keyword_search_uses_repository_filtering():
    service = SearchService(activity_repository=FakeActivityRepository())

    results = service.keyword_search(user_id=123, query="hills")

    assert len(results) == 1
    assert results[0].strava_activity_id == 1


def test_semantic_search_scores_relevant_activity_first():
    service = SearchService(activity_repository=FakeActivityRepository())

    results = service.semantic_search(user_id=123, query="run hills")

    assert [result.strava_activity_id for result in results] == [1]
    assert results[0].score == 1.0