from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.diary import get_diary_service
from app.main import app


class FakeDiaryService:
    def list_entries(self, *, user_id):
        return [
            SimpleNamespace(
                id=uuid4(),
                strava_activity_id=123,
                name="Diary Entry",
                type="Run",
                start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
                distance=10000.0,
                description="Morning diary entry",
                location_country="GB",
                model_dump=lambda: {
                    "id": str(uuid4()),
                    "strava_activity_id": 123,
                    "name": "Diary Entry",
                    "type": "Run",
                    "start_date": datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc).isoformat(),
                    "distance": 10000.0,
                    "description": "Morning diary entry",
                    "location_country": "GB",
                },
            )
        ]


def test_diary_endpoint_returns_entries():
    app.dependency_overrides[get_diary_service] = lambda: FakeDiaryService()
    client = TestClient(app)

    response = client.get("/diary?strava_athlete_id=123")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["entries"][0]["strava_activity_id"] == 123