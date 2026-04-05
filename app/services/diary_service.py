from __future__ import annotations

from dataclasses import dataclass

from app.db.repositories.activity_repo import ActivityRepository
from app.schemas.diary import DiaryEntry


@dataclass(frozen=True)
class DiaryService:
    activity_repository: ActivityRepository

    def list_entries(self, *, user_id) -> list[DiaryEntry]:
        activities = self.activity_repository.list_by_user_id(user_id=user_id)
        return [
            DiaryEntry(
                id=activity.id,
                strava_activity_id=activity.strava_activity_id,
                name=activity.name,
                type=activity.type,
                start_date=activity.start_date,
                distance=float(activity.distance) if activity.distance is not None else None,
                description=activity.description,
                location_country=activity.location_country,
            )
            for activity in activities
        ]
