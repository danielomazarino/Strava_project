from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


TokenHealth = Literal['active', 'expiring', 'expired']


class AdminActivitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_strava_athlete_id: int
    strava_activity_id: int
    name: str | None = None
    type: str | None = None
    start_date: datetime
    distance: float | None = None
    moving_time: int | None = None
    elapsed_time: int | None = None
    elevation_gain: float | None = None
    description: str | None = None
    polyline: str | None = None
    timezone: str | None = None
    location_country: str | None = None
    has_raw_payload: bool
    token_health: TokenHealth
    raw_payload: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    strava_athlete_id: int
    token_expires_at: datetime
    token_health: TokenHealth
    activity_count: int
    latest_activity_start_date: datetime | None = None
    latest_activity_name: str | None = None
    latest_activity_country: str | None = None


class AdminTotals(BaseModel):
    users: int
    activities: int
    active_tokens: int
    expiring_tokens: int
    expired_tokens: int


class AdminOverviewResponse(BaseModel):
    status: Literal['ok'] = 'ok'
    generated_at: datetime
    totals: AdminTotals
    users: list[AdminUserSummary]
    recent_activities: list[AdminActivitySummary]
    records: list[AdminActivitySummary]