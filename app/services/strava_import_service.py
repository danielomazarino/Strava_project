from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import Settings
from app.core.security import decrypt_secret
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository


class StravaImportService:
    def __init__(
        self,
        *,
        settings: Settings,
        user_repository: UserRepository,
        activity_repository: ActivityRepository,
        http_client: httpx.Client,
        activity_list_url: str = "https://www.strava.com/api/v3/athlete/activities",
        activity_detail_url: str = "https://www.strava.com/api/v3/activities",
    ):
        self.settings = settings
        self.user_repository = user_repository
        self.activity_repository = activity_repository
        self.http_client = http_client
        self.activity_list_url = activity_list_url
        self.activity_detail_url = activity_detail_url

    def import_activities(
        self,
        *,
        strava_athlete_id: int,
        after: int | None = None,
        before: int | None = None,
        per_page: int = 200,
    ) -> int:
        user = self.user_repository.get_by_strava_athlete_id(strava_athlete_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        access_token = decrypt_secret(user.access_token_encrypted, self.settings.secret_key)
        total_imported = 0
        page = 1

        while True:
            activities = self._fetch_activity_page(
                access_token=access_token,
                page=page,
                per_page=per_page,
                after=after,
                before=before,
            )
            if not activities:
                break

            for summary_activity in activities:
                activity_detail = self._fetch_activity_detail(
                    access_token=access_token,
                    activity_id=int(summary_activity["id"]),
                )
                self.activity_repository.upsert_activity(
                    user_id=user.id,
                    strava_activity_id=int(activity_detail["id"]),
                    name=activity_detail.get("name"),
                    type=activity_detail.get("type"),
                    start_date=self._parse_datetime(activity_detail["start_date"]),
                    distance=activity_detail.get("distance"),
                    moving_time=activity_detail.get("moving_time"),
                    elapsed_time=activity_detail.get("elapsed_time"),
                    elevation_gain=activity_detail.get("total_elevation_gain"),
                    description=activity_detail.get("description"),
                    polyline=self._extract_polyline(activity_detail),
                    timezone=activity_detail.get("timezone"),
                    location_country=activity_detail.get("location_country"),
                    raw_payload=activity_detail,
                )
                total_imported += 1

            page += 1

        return total_imported

    def _fetch_activity_page(
        self,
        *,
        access_token: str,
        page: int,
        per_page: int,
        after: int | None,
        before: int | None,
    ) -> list[dict[str, Any]]:
        params: dict[str, int] = {"page": page, "per_page": per_page}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before

        response = self.http_client.get(
            self.activity_list_url,
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Invalid Strava activity list response")
        return payload

    def _fetch_activity_detail(self, *, access_token: str, activity_id: int) -> dict[str, Any]:
        response = self.http_client.get(
            f"{self.activity_detail_url}/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Invalid Strava activity detail response")
        return payload

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        parsed_value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed_value.tzinfo is None:
            return parsed_value.replace(tzinfo=timezone.utc)
        return parsed_value

    @staticmethod
    def _extract_polyline(payload: dict[str, Any]) -> str | None:
        map_data = payload.get("map")
        if isinstance(map_data, dict):
            polyline = map_data.get("summary_polyline")
            if polyline is not None:
                return str(polyline)
        return payload.get("polyline")