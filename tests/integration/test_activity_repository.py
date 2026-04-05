from datetime import datetime, timezone

from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository


def test_activity_repository_upserts_by_user_and_strava_activity_id(sqlite_session):
    user_repository = UserRepository(sqlite_session)
    activity_repository = ActivityRepository(sqlite_session)
    user = user_repository.upsert_tokens(
        strava_athlete_id=777,
        access_token="access-token",
        refresh_token="refresh-token",
        token_expires_at=datetime.now(timezone.utc),
        secret_key="integration-secret",
    )

    first = activity_repository.upsert_activity(
        user_id=user.id,
        strava_activity_id=333,
        name="Initial Name",
        type="Run",
        start_date=datetime(2026, 4, 5, 9, 0, tzinfo=timezone.utc),
        distance=5_000,
        moving_time=1_800,
        elapsed_time=1_900,
        elevation_gain=45,
        description="First pass",
        polyline="polyline-a",
        timezone="UTC",
        location_country="GB",
        raw_payload={"id": 333, "name": "Initial Name"},
    )

    second = activity_repository.upsert_activity(
        user_id=user.id,
        strava_activity_id=333,
        name="Updated Name",
        type="Run",
        start_date=datetime(2026, 4, 5, 9, 0, tzinfo=timezone.utc),
        distance=5_200,
        moving_time=1_850,
        elapsed_time=1_950,
        elevation_gain=50,
        description="Updated pass",
        polyline="polyline-b",
        timezone="UTC",
        location_country="GB",
        raw_payload={"id": 333, "name": "Updated Name"},
    )

    assert first.id == second.id
    assert second.name == "Updated Name"