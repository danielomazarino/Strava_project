from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SearchResult(BaseModel):
    id: UUID
    strava_activity_id: int
    name: str | None = None
    type: str | None = None
    start_date: datetime
    score: float | None = None
