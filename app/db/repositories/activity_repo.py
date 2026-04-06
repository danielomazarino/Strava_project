from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db.models.activity import Activity


class ActivityRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_user_and_strava_activity_id(
        self,
        *,
        user_id,
        strava_activity_id: int,
    ) -> Activity | None:
        statement = select(Activity).where(
            and_(
                Activity.user_id == user_id,
                Activity.strava_activity_id == strava_activity_id,
            )
        )
        return self.session.execute(statement).scalars().one_or_none()

    def upsert_activity(
        self,
        *,
        user_id,
        strava_activity_id: int,
        name: str | None,
        type: str | None,
        start_date: datetime,
        distance,
        moving_time,
        elapsed_time,
        elevation_gain,
        description: str | None,
        polyline: str | None,
        timezone: str | None,
        location_country: str | None,
        raw_payload: dict | None,
    ) -> Activity:
        activity = self.get_by_user_and_strava_activity_id(
            user_id=user_id,
            strava_activity_id=strava_activity_id,
        )

        if activity is None:
            activity = Activity(
                user_id=user_id,
                strava_activity_id=strava_activity_id,
                name=name,
                type=type,
                start_date=start_date,
                distance=distance,
                moving_time=moving_time,
                elapsed_time=elapsed_time,
                elevation_gain=elevation_gain,
                description=description,
                polyline=polyline,
                timezone=timezone,
                location_country=location_country,
                raw_payload=raw_payload,
            )
            self.session.add(activity)
        else:
            activity.name = name
            activity.type = type
            activity.start_date = start_date
            activity.distance = distance
            activity.moving_time = moving_time
            activity.elapsed_time = elapsed_time
            activity.elevation_gain = elevation_gain
            activity.description = description
            activity.polyline = polyline
            activity.timezone = timezone
            activity.location_country = location_country
            activity.raw_payload = raw_payload

        self.session.flush()
        self.session.commit()
        return activity

    def list_by_user_id(self, *, user_id) -> list[Activity]:
        statement = select(Activity).where(Activity.user_id == user_id).order_by(Activity.start_date.desc())
        return list(self.session.execute(statement).scalars().all())

    def search_by_user_id(self, *, user_id, query: str) -> list[Activity]:
        search_term = f"%{query.lower()}%"
        statement = (
            select(Activity)
            .where(
                Activity.user_id == user_id,
                or_(
                    Activity.name.is_not(None) & Activity.name.ilike(search_term),
                    Activity.type.is_not(None) & Activity.type.ilike(search_term),
                    Activity.description.is_not(None) & Activity.description.ilike(search_term),
                    Activity.location_country.is_not(None) & Activity.location_country.ilike(search_term),
                ),
            )
            .order_by(Activity.start_date.desc())
        )
        return list(self.session.execute(statement).scalars().all())

    def list_by_user_id_between_dates(
        self,
        *,
        user_id,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Activity]:
        statement = (
            select(Activity)
            .where(
                Activity.user_id == user_id,
                Activity.start_date >= start_date,
                Activity.start_date <= end_date,
            )
            .order_by(Activity.start_date.asc(), Activity.id.asc())
        )
        return list(self.session.execute(statement).scalars().all())

    def list_by_user_id_and_country(
        self,
        *,
        user_id,
        country: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Activity]:
        conditions = [
            Activity.user_id == user_id,
            Activity.location_country == country,
        ]
        if start_date is not None:
            conditions.append(Activity.start_date >= start_date)
        if end_date is not None:
            conditions.append(Activity.start_date <= end_date)

        statement = (
            select(Activity)
            .where(*conditions)
            .order_by(Activity.start_date.asc(), Activity.id.asc())
        )
        return list(self.session.execute(statement).scalars().all())

    def get_latest_start_date_for_user(self, *, user_id) -> datetime | None:
        statement = (
            select(Activity.start_date)
            .where(Activity.user_id == user_id)
            .order_by(Activity.start_date.desc(), Activity.id.desc())
            .limit(1)
        )
        return self.session.execute(statement).scalars().one_or_none()