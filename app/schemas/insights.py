from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SummaryInsight(BaseModel):
    summary: str
    volume: str | None = None
    intensity: str | None = None
    notable_events: list[str] = Field(default_factory=list)
    subjective_notes: list[str] = Field(default_factory=list)
    performance_patterns: list[str] = Field(default_factory=list)


class PatternInsight(BaseModel):
    patterns: list[str] = Field(default_factory=list)
    fatigue: list[str] = Field(default_factory=list)
    motivation: list[str] = Field(default_factory=list)
    terrain_effects: list[str] = Field(default_factory=list)
    weather_effects: list[str] = Field(default_factory=list)
    pacing_issues: list[str] = Field(default_factory=list)


class RegionComparisonInsight(BaseModel):
    region_a: str
    region_b: str
    perceived_effort: str
    terrain_differences: list[str] = Field(default_factory=list)
    pacing_differences: list[str] = Field(default_factory=list)
    subjective_notes: list[str] = Field(default_factory=list)


class ActivityInsightItem(BaseModel):
    id: UUID
    strava_activity_id: int
    name: str | None = None
    type: str | None = None
    start_date: datetime
    description: str | None = None
    location_country: str | None = None
