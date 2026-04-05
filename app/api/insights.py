from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.activities import get_activity_repository as get_activity_repository_from_activities
from app.api.auth import get_user_repository
from app.core.config import Settings, get_settings
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.services.llm_service import LLMService, StubLLMModelClient

router = APIRouter(prefix="/insights", tags=["insights"])


def get_llm_service(
    settings: Settings = Depends(get_settings),
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository_from_activities),
) -> LLMService:
    return LLMService(
        settings=settings,
        user_repository=user_repository,
        activity_repository=activity_repository,
        model_client=StubLLMModelClient(),
    )


@router.get("/summary")
async def summary(
    strava_athlete_id: int,
    start_date: datetime,
    end_date: datetime,
    llm_service: LLMService = Depends(get_llm_service),
) -> dict[str, object]:
    analysis = await llm_service.summarize_period(
        strava_athlete_id=strava_athlete_id,
        start_date=start_date,
        end_date=end_date,
    )
    return {"status": "ok", "analysis": analysis.model_dump()}


@router.get("/patterns")
async def patterns(
    strava_athlete_id: int,
    start_date: datetime,
    end_date: datetime,
    llm_service: LLMService = Depends(get_llm_service),
) -> dict[str, object]:
    analysis = await llm_service.detect_patterns(
        strava_athlete_id=strava_athlete_id,
        start_date=start_date,
        end_date=end_date,
    )
    return {"status": "ok", "analysis": analysis.model_dump()}


@router.get("/regions/comparison")
async def region_comparison(
    strava_athlete_id: int,
    region_a: str,
    region_b: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    llm_service: LLMService = Depends(get_llm_service),
) -> dict[str, object]:
    analysis = await llm_service.compare_regions(
        strava_athlete_id=strava_athlete_id,
        region_a=region_a,
        region_b=region_b,
        start_date=start_date,
        end_date=end_date,
    )
    return {"status": "ok", "analysis": analysis.model_dump()}
