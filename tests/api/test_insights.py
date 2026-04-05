from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.insights import get_llm_service
from app.main import app


class FakeLLMService:
    async def summarize_period(self, *, strava_athlete_id, start_date, end_date):
        return SimpleNamespace(
            model_dump=lambda: {
                "summary": "Good week",
                "volume": "high",
                "intensity": "moderate",
                "notable_events": ["Long run"],
                "subjective_notes": ["Felt strong"],
                "performance_patterns": ["Held pace well"],
            }
        )

    async def detect_patterns(self, *, strava_athlete_id, start_date, end_date):
        return SimpleNamespace(
            model_dump=lambda: {
                "patterns": ["Late week fatigue"],
                "fatigue": ["Late week fatigue"],
                "motivation": ["Stable"],
                "terrain_effects": ["Hills mattered"],
                "weather_effects": ["Windy"],
                "pacing_issues": ["Started fast"],
            }
        )

    async def compare_regions(self, *, strava_athlete_id, region_a, region_b, start_date=None, end_date=None):
        return SimpleNamespace(
            model_dump=lambda: {
                "region_a": region_a,
                "region_b": region_b,
                "perceived_effort": "higher in GB",
                "terrain_differences": ["GB was hillier"],
                "pacing_differences": ["FR was steadier"],
                "subjective_notes": ["Liked both"],
            }
        )


def test_summary_endpoint_returns_analysis():
    app.dependency_overrides[get_llm_service] = lambda: FakeLLMService()
    client = TestClient(app)

    response = client.get(
        "/insights/summary?strava_athlete_id=123&start_date=2026-04-01T00:00:00Z&end_date=2026-04-30T00:00:00Z"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["analysis"]["summary"] == "Good week"


def test_pattern_endpoint_returns_analysis():
    app.dependency_overrides[get_llm_service] = lambda: FakeLLMService()
    client = TestClient(app)

    response = client.get(
        "/insights/patterns?strava_athlete_id=123&start_date=2026-04-01T00:00:00Z&end_date=2026-04-30T00:00:00Z"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["analysis"]["patterns"] == ["Late week fatigue"]


def test_region_comparison_endpoint_returns_analysis():
    app.dependency_overrides[get_llm_service] = lambda: FakeLLMService()
    client = TestClient(app)

    response = client.get("/insights/regions/comparison?strava_athlete_id=123&region_a=GB&region_b=FR")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["analysis"]["region_a"] == "GB"
