from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings, is_production_environment
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.schemas.admin import AdminActivitySummary, AdminOverviewResponse, AdminTotals, AdminUserSummary

router = APIRouter(prefix='/admin', tags=['admin'])


def get_http_client() -> Generator[httpx.Client, None, None]:
    client = httpx.Client(timeout=10.0)
    try:
        yield client
    finally:
        client.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


@router.get('/overview')
def get_overview(
    settings: Settings = Depends(get_settings),
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
) -> dict[str, object]:
    if is_production_environment(settings):
        raise HTTPException(status_code=404, detail='Not found')

    now = datetime.now(timezone.utc)
    users = user_repository.list_all_users()
    user_summaries: list[AdminUserSummary] = []
    recent_activities: list[AdminActivitySummary] = []
    all_records: list[AdminActivitySummary] = []
    total_activities = 0
    active_tokens = 0
    expiring_tokens = 0
    expired_tokens = 0

    for user in users:
        activities = activity_repository.list_by_user_id(user_id=user.id)
        total_activities += len(activities)

        latest_activity = activities[0] if activities else None
        token_expires_at = ensure_utc(user.token_expires_at)
        if token_expires_at <= now:
            token_health = 'expired'
            expired_tokens += 1
        elif token_expires_at <= now + timedelta(hours=1):
            token_health = 'expiring'
            expiring_tokens += 1
            active_tokens += 1
        else:
            token_health = 'active'
            active_tokens += 1

        user_summaries.append(
            AdminUserSummary(
                id=user.id,
                strava_athlete_id=user.strava_athlete_id,
                token_expires_at=token_expires_at,
                token_health=token_health,
                activity_count=len(activities),
                latest_activity_start_date=latest_activity.start_date if latest_activity else None,
                latest_activity_name=latest_activity.name if latest_activity else None,
                latest_activity_country=latest_activity.location_country if latest_activity else None,
            )
        )

        for activity in activities:
            recent_activities.append(
                AdminActivitySummary(
                    id=activity.id,
                    user_id=user.id,
                    user_strava_athlete_id=user.strava_athlete_id,
                    strava_activity_id=activity.strava_activity_id,
                    name=activity.name,
                    type=activity.type,
                    start_date=activity.start_date,
                    distance=activity.distance,
                    moving_time=activity.moving_time,
                    elapsed_time=activity.elapsed_time,
                    elevation_gain=activity.elevation_gain,
                    description=activity.description,
                    polyline=activity.polyline,
                    timezone=activity.timezone,
                    location_country=activity.location_country,
                    has_raw_payload=activity.raw_payload is not None,
                    token_health=token_health,
                    raw_payload=activity.raw_payload,
                    created_at=activity.created_at,
                    updated_at=activity.updated_at,
                )
            )

            all_records.append(recent_activities[-1])

    recent_activities.sort(key=lambda item: item.start_date, reverse=True)
    all_records.sort(key=lambda item: item.start_date, reverse=True)

    overview = AdminOverviewResponse(
        generated_at=now,
        totals=AdminTotals(
            users=len(users),
            activities=total_activities,
            active_tokens=active_tokens,
            expiring_tokens=expiring_tokens,
            expired_tokens=expired_tokens,
        ),
        users=user_summaries,
        recent_activities=recent_activities[:12],
        records=all_records,
    )
    return overview.model_dump(mode='json')