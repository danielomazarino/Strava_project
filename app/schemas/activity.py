from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
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
    raw_payload: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None