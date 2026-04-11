from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.security import encrypt_secret
from app.db.base import Base
from app.db.models.activity import Activity
from app.db.models.user import User

import app.db.models  # noqa: F401


DEV_DEMO_STRAVA_ATHLETE_ID = 14706324
DEV_DEMO_ACCESS_TOKEN = 'dev-demo-access-token'
DEV_DEMO_REFRESH_TOKEN = 'dev-demo-refresh-token'
DEV_DEMO_SECRET_KEY = 'development-demo-secret'
DEV_DEMO_POLYLINE = '_leiI_y|u@owHowHowHowH~{BowH~uJowH'


def initialize_database(database_url: str) -> None:
    if not database_url:
        return

    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        Base.metadata.create_all(engine)
    finally:
        engine.dispose()


def seed_development_database(database_url: str, *, secret_key: str | None = None) -> None:
    if not database_url:
        return

    engine = create_engine(database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        user = session.execute(
            select(User).where(User.strava_athlete_id == DEV_DEMO_STRAVA_ATHLETE_ID)
        ).scalars().one_or_none()
        if user is None:
            resolved_secret_key = secret_key or DEV_DEMO_SECRET_KEY
            user = User(
                strava_athlete_id=DEV_DEMO_STRAVA_ATHLETE_ID,
                access_token_encrypted=encrypt_secret(DEV_DEMO_ACCESS_TOKEN, resolved_secret_key),
                refresh_token_encrypted=encrypt_secret(DEV_DEMO_REFRESH_TOKEN, resolved_secret_key),
                token_expires_at=datetime.now(timezone.utc) + timedelta(days=45),
            )
            session.add(user)
            session.flush()

        existing_activity_ids = set(
            session.execute(
                select(Activity.strava_activity_id).where(Activity.user_id == user.id)
            ).scalars().all()
        )

        for activity in session.execute(select(Activity).where(Activity.user_id == user.id)).scalars():
            raw_payload = activity.raw_payload or {}
            if isinstance(raw_payload, dict) and raw_payload.get('seed'):
                activity.polyline = DEV_DEMO_POLYLINE

        seed_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        activity_specs = [
            {
                "strava_activity_id": 9100008,
                "days_ago": 1,
                "name": "Recovery Run",
                "type": "Run",
                "distance": 8400,
                "moving_time": 2340,
                "elapsed_time": 2400,
                "elevation_gain": 68,
                "description": "Easy movement to keep the legs fresh.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Stockholm",
                "location_country": "SE",
                "raw_payload": {"seed": True, "kind": "recovery"},
            },
            {
                "strava_activity_id": 9100007,
                "days_ago": 3,
                "name": "Threshold Intervals",
                "type": "Run",
                "distance": 12650,
                "moving_time": 3880,
                "elapsed_time": 3970,
                "elevation_gain": 146,
                "description": "Controlled hard work with short recoveries.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Stockholm",
                "location_country": "SE",
                "raw_payload": {"seed": True, "kind": "intervals"},
            },
            {
                "strava_activity_id": 9100006,
                "days_ago": 5,
                "name": "Endurance Ride",
                "type": "Ride",
                "distance": 42800,
                "moving_time": 8210,
                "elapsed_time": 8580,
                "elevation_gain": 512,
                "description": "Long steady ride on mixed roads.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Stockholm",
                "location_country": "SE",
                "raw_payload": {"seed": True, "kind": "ride"},
            },
            {
                "strava_activity_id": 9100005,
                "days_ago": 8,
                "name": "Trail Run",
                "type": "Run",
                "distance": 15400,
                "moving_time": 4920,
                "elapsed_time": 5070,
                "elevation_gain": 284,
                "description": "Rolling terrain and a few technical sections.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Oslo",
                "location_country": "NO",
                "raw_payload": {"seed": True, "kind": "trail"},
            },
            {
                "strava_activity_id": 9100004,
                "days_ago": 11,
                "name": "Tempo Session",
                "type": "Run",
                "distance": 10100,
                "moving_time": 3100,
                "elapsed_time": 3170,
                "elevation_gain": 92,
                "description": "Comfortably hard work with even pacing.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Copenhagen",
                "location_country": "DK",
                "raw_payload": {"seed": True, "kind": "tempo"},
            },
            {
                "strava_activity_id": 9100003,
                "days_ago": 14,
                "name": "Commute Spin",
                "type": "Ride",
                "distance": 18600,
                "moving_time": 2440,
                "elapsed_time": 2550,
                "elevation_gain": 61,
                "description": "Light spin to and from the office.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Stockholm",
                "location_country": "SE",
                "raw_payload": {"seed": True, "kind": "commute"},
            },
            {
                "strava_activity_id": 9100002,
                "days_ago": 18,
                "name": "Long Run",
                "type": "Run",
                "distance": 21800,
                "moving_time": 6330,
                "elapsed_time": 6470,
                "elevation_gain": 168,
                "description": "The weekly long session with an aerobic finish.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Stockholm",
                "location_country": "SE",
                "raw_payload": {"seed": True, "kind": "long-run"},
            },
            {
                "strava_activity_id": 9100001,
                "days_ago": 24,
                "name": "Progression Run",
                "type": "Run",
                "distance": 13400,
                "moving_time": 4010,
                "elapsed_time": 4090,
                "elevation_gain": 104,
                "description": "Starts easy and closes with stronger running.",
                "polyline": DEV_DEMO_POLYLINE,
                "timezone": "Europe/Helsinki",
                "location_country": "FI",
                "raw_payload": {"seed": True, "kind": "progression"},
            },
        ]

        for activity_spec in activity_specs:
            if activity_spec["strava_activity_id"] in existing_activity_ids:
                continue

            activity = Activity(
                user_id=user.id,
                strava_activity_id=activity_spec["strava_activity_id"],
                name=activity_spec["name"],
                type=activity_spec["type"],
                start_date=seed_time - timedelta(days=activity_spec["days_ago"]),
                distance=activity_spec["distance"],
                moving_time=activity_spec["moving_time"],
                elapsed_time=activity_spec["elapsed_time"],
                elevation_gain=activity_spec["elevation_gain"],
                description=activity_spec["description"],
                polyline=activity_spec["polyline"],
                timezone=activity_spec["timezone"],
                location_country=activity_spec["location_country"],
                raw_payload=activity_spec["raw_payload"],
            )
            session.add(activity)

        session.commit()
    finally:
        session.close()
        engine.dispose()