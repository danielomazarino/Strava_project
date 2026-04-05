from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.repositories.activity_repo import ActivityRepository
from app.db.session import get_db
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def get_search_service(
    activity_repository: ActivityRepository = Depends(get_activity_repository),
) -> SearchService:
    return SearchService(activity_repository=activity_repository)


@router.get("/keyword")
def keyword_search(
    strava_athlete_id: int,
    q: str,
    search_service: SearchService = Depends(get_search_service),
) -> dict[str, object]:
    results = search_service.keyword_search(user_id=strava_athlete_id, query=q)
    return {"status": "ok", "results": [result.model_dump() for result in results]}


@router.get("/semantic")
def semantic_search(
    strava_athlete_id: int,
    q: str,
    search_service: SearchService = Depends(get_search_service),
) -> dict[str, object]:
    results = search_service.semantic_search(user_id=strava_athlete_id, query=q)
    return {"status": "ok", "results": [result.model_dump() for result in results]}