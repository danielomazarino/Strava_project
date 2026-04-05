from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.search import get_search_service
from app.main import app


class FakeSearchService:
    def keyword_search(self, *, user_id, query: str):
        return [
            SimpleNamespace(
                id=uuid4(),
                strava_activity_id=321,
                name="Keyword Match",
                type="Run",
                start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
                score=1.0,
                model_dump=lambda: {
                    "id": str(uuid4()),
                    "strava_activity_id": 321,
                    "name": "Keyword Match",
                    "type": "Run",
                    "start_date": datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc).isoformat(),
                    "score": 1.0,
                },
            )
        ]

    def semantic_search(self, *, user_id, query: str):
        return [
            SimpleNamespace(
                id=uuid4(),
                strava_activity_id=654,
                name="Semantic Match",
                type="Ride",
                start_date=datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc),
                score=0.5,
                model_dump=lambda: {
                    "id": str(uuid4()),
                    "strava_activity_id": 654,
                    "name": "Semantic Match",
                    "type": "Ride",
                    "start_date": datetime(2026, 4, 4, 8, 0, tzinfo=timezone.utc).isoformat(),
                    "score": 0.5,
                },
            )
        ]


def test_keyword_search_endpoint_returns_results():
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()
    client = TestClient(app)

    response = client.get("/search/keyword?strava_athlete_id=123&q=hills")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["results"][0]["strava_activity_id"] == 321


def test_semantic_search_endpoint_returns_results():
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()
    client = TestClient(app)

    response = client.get("/search/semantic?strava_athlete_id=123&q=ride")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["results"][0]["strava_activity_id"] == 654