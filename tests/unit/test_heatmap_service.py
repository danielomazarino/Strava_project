from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.heatmap_service import HeatmapService


@dataclass
class FakeActivity:
    id: object
    strava_activity_id: int
    polyline: str
    start_date: datetime
    type: str
    location_country: str


class FakeUserRepository:
    def get_by_strava_athlete_id(self, strava_athlete_id: int):
        return SimpleNamespace(id=uuid4(), strava_athlete_id=strava_athlete_id)


class FakeActivityRepository:
    def __init__(self, activities: list[FakeActivity]):
        self.activities = activities
        self.calls: list[dict] = []

    def list_by_user_id(self, *, user_id):
        self.calls.append({"user_id": user_id})
        return self.activities


@pytest.fixture()
def heatmap_service():
    polyline = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
    activities = [
        FakeActivity(
            id=uuid4(),
            strava_activity_id=101,
            polyline=polyline,
            start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
            type="Run",
            location_country="GB",
        ),
        FakeActivity(
            id=uuid4(),
            strava_activity_id=102,
            polyline="",
            start_date=datetime(2026, 4, 6, 8, 0, tzinfo=timezone.utc),
            type="Ride",
            location_country="FR",
        ),
    ]
    return HeatmapService(
        user_repository=FakeUserRepository(),
        activity_repository=FakeActivityRepository(activities),
    )


def test_decode_polyline_returns_expected_points(heatmap_service):
    points = heatmap_service.decode_polyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@")

    assert len(points) == 3
    assert points[0].lat == pytest.approx(38.5)
    assert points[0].lng == pytest.approx(-120.2)
    assert points[2].lat == pytest.approx(43.252)
    assert points[2].lng == pytest.approx(-126.453)


def test_extract_geo_data_builds_bbox(heatmap_service):
    activity = heatmap_service.activity_repository.activities[0]

    geo_data = heatmap_service.extract_geo_data(activity)

    assert geo_data.point_count == 3
    assert geo_data.bounding_box is not None
    assert geo_data.bounding_box.min_lat == pytest.approx(38.5)
    assert geo_data.bounding_box.max_lng == pytest.approx(-120.2)


def test_build_tile_filters_by_activity_type_and_country(heatmap_service):
    tile = heatmap_service.build_tile(
        strava_athlete_id=123,
        z=0,
        x=0,
        y=0,
        activity_type="Run",
        country="GB",
    )

    assert tile.point_count == 3
    assert tile.activity_count == 1
    assert tile.z == 0
    assert tile.bounds.min_lat < tile.bounds.max_lat


def test_build_tile_skips_non_matching_activity_type(heatmap_service):
    tile = heatmap_service.build_tile(
        strava_athlete_id=123,
        z=0,
        x=0,
        y=0,
        activity_type="Swim",
    )

    assert tile.point_count == 0
    assert tile.activity_count == 0
