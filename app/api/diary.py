from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.services.diary_service import DiaryService

router = APIRouter(prefix="/diary", tags=["diary"])


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_diary_service(
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
) -> DiaryService:
    return DiaryService(user_repository=user_repository, activity_repository=activity_repository)


@router.get("")
def list_diary_entries(
    strava_athlete_id: int,
    diary_service: DiaryService = Depends(get_diary_service),
) -> dict[str, object]:
    entries = diary_service.list_entries(strava_athlete_id=strava_athlete_id)
    return {"status": "ok", "entries": [entry.model_dump() for entry in entries]}
