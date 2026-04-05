from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.activities import get_activity_repository as get_activity_repository_from_activities
from app.api.auth import get_user_repository
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.services.heatmap_service import HeatmapService

router = APIRouter(prefix="/heatmaps", tags=["heatmaps"])


def get_heatmap_service(
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository_from_activities),
) -> HeatmapService:
    return HeatmapService(
        user_repository=user_repository,
        activity_repository=activity_repository,
    )


@router.get("/tiles/{z}/{x}/{y}")
def tile(
    z: int,
    x: int,
    y: int,
    strava_athlete_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    activity_type: str | None = None,
    country: str | None = None,
    heatmap_service: HeatmapService = Depends(get_heatmap_service),
) -> dict[str, object]:
    tile_data = heatmap_service.build_tile(
        strava_athlete_id=strava_athlete_id,
        z=z,
        x=x,
        y=y,
        start_date=start_date,
        end_date=end_date,
        activity_type=activity_type,
        country=country,
    )
    return {"status": "ok", "tile": tile_data.model_dump()}
