from __future__ import annotations

from collections.abc import Generator

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.schemas.activity import ActivityDetail
from app.services.strava_import_service import StravaImportService

router = APIRouter(prefix="/activities", tags=["activities"])


def get_http_client() -> Generator[httpx.Client, None, None]:
    client = httpx.Client(timeout=20.0)
    try:
        yield client
    finally:
        client.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def get_strava_import_service(
    settings: Settings = Depends(get_settings),
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
    http_client: httpx.Client = Depends(get_http_client),
) -> StravaImportService:
    return StravaImportService(
        settings=settings,
        user_repository=user_repository,
        activity_repository=activity_repository,
        http_client=http_client,
    )


@router.post("/import")
def import_activities(
    strava_athlete_id: int,
    after: int | None = None,
    before: int | None = None,
    import_service: StravaImportService = Depends(get_strava_import_service),
) -> dict[str, int | str]:
    imported_count = import_service.import_activities(
        strava_athlete_id=strava_athlete_id,
        after=after,
        before=before,
    )
    return {"status": "ok", "imported": imported_count}


@router.get("/{strava_activity_id}")
def get_activity(
    strava_activity_id: int,
    strava_athlete_id: int,
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
) -> dict[str, object]:
    user = user_repository.get_by_strava_athlete_id(strava_athlete_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    activity = activity_repository.get_by_user_and_strava_activity_id(
        user_id=user.id,
        strava_activity_id=strava_activity_id,
    )
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    return {"status": "ok", "activity": ActivityDetail.model_validate(activity).model_dump(mode="json")}