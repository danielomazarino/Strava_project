from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DiaryEntry(BaseModel):
    id: UUID
    strava_activity_id: int
    name: str | None = None
    type: str | None = None
    start_date: datetime
    distance: float | None = None
    description: str | None = None
    location_country: str | None = None
