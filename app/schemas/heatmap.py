from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    lat: float
    lng: float


class GeoBounds(BaseModel):
    min_lat: float
    min_lng: float
    max_lat: float
    max_lng: float


class ActivityGeoData(BaseModel):
    activity_id: UUID
    strava_activity_id: int
    point_count: int
    bounding_box: GeoBounds | None = None
    points: list[GeoPoint] = Field(default_factory=list)


class HeatmapTilePoint(BaseModel):
    activity_id: UUID
    strava_activity_id: int
    lat: float
    lng: float


class HeatmapTile(BaseModel):
    z: int
    x: int
    y: int
    point_count: int
    activity_count: int
    bounds: GeoBounds
    generated_at: datetime
    points: list[HeatmapTilePoint] = Field(default_factory=list)
