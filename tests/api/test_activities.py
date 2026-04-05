from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.activities import get_strava_import_service
from app.main import app


class FakeImportService:
    def import_activities(self, *, strava_athlete_id: int, after=None, before=None):
        return 3


def test_import_endpoint_returns_import_count():
    app.dependency_overrides[get_strava_import_service] = lambda: FakeImportService()
    client = TestClient(app)

    response = client.post("/activities/import?strava_athlete_id=123")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "imported": 3}