from __future__ import annotations

from dataclasses import dataclass

from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.diary import DiaryEntry


@dataclass(frozen=True)
class DiaryService:
    user_repository: UserRepository
    activity_repository: ActivityRepository

    def list_entries(self, *, strava_athlete_id: int) -> list[DiaryEntry]:
        user = self.user_repository.get_by_strava_athlete_id(strava_athlete_id)
        if user is None:
            raise ValueError("User not found")

        activities = self.activity_repository.list_by_user_id(user_id=user.id)
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
