from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.heatmaps import get_heatmap_service
from app.main import app


class FakeHeatmapService:
    def build_tile(self, *, strava_athlete_id, z, x, y, start_date=None, end_date=None, activity_type=None, country=None):
        return SimpleNamespace(
            model_dump=lambda: {
                "z": z,
                "x": x,
                "y": y,
                "point_count": 2,
                "activity_count": 1,
                "bounds": {
                    "min_lat": 10.0,
                    "min_lng": 10.0,
                    "max_lat": 11.0,
                    "max_lng": 11.0,
                },
                "generated_at": datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc).isoformat(),
                "points": [
                    {
                        "activity_id": "00000000-0000-0000-0000-000000000001",
                        "strava_activity_id": 101,
                        "lat": 10.5,
                        "lng": 10.5,
                    }
                ],
            }
        )


def test_heatmap_tile_endpoint_returns_tile_payload():
    app.dependency_overrides[get_heatmap_service] = lambda: FakeHeatmapService()
    client = TestClient(app)

    response = client.get("/heatmaps/tiles/0/0/0?strava_athlete_id=123&activity_type=Run&country=GB")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["tile"]["point_count"] == 2
    assert response.json()["tile"]["activity_count"] == 1
