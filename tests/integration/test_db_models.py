from datetime import datetime, timezone

from app.db.models.activity import Activity
from app.db.repositories.user_repo import UserRepository


def test_user_and_activity_models_persist(sqlite_session):
    repository = UserRepository(sqlite_session)
    user = repository.upsert_tokens(
        strava_athlete_id=555,
        access_token="access-token",
        refresh_token="refresh-token",
        token_expires_at=datetime.now(timezone.utc),
        secret_key="integration-secret",
    )

    activity = Activity(
        user_id=user.id,
        strava_activity_id=999,
        name="Morning Run",
        type="Run",
        start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
        distance=10_000,
        moving_time=3_600,
        elapsed_time=3_700,
        elevation_gain=120,
        description="Easy session",
        polyline="encoded-polyline",
        timezone="UTC",
        location_country="GB",
        raw_payload={"id": 999},
    )
    sqlite_session.add(activity)
    sqlite_session.commit()
    sqlite_session.refresh(activity)

    persisted_activity = sqlite_session.query(Activity).one()

    assert persisted_activity.user_id == user.id
    assert persisted_activity.strava_activity_id == 999
    assert persisted_activity.name == "Morning Run"