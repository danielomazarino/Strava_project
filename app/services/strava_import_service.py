from __future__ import annotations

from datetime import datetime, timezone
from time import sleep
from typing import Callable, Any

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
        sleep_fn: Callable[[int], None] = sleep,
    ):
        self.settings = settings
        self.user_repository = user_repository
        self.activity_repository = activity_repository
        self.http_client = http_client
        self.activity_list_url = activity_list_url
        self.sleep_fn = sleep_fn

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
                self.activity_repository.upsert_activity(
                    user_id=user.id,
                    strava_activity_id=int(summary_activity["id"]),
                    name=summary_activity.get("name"),
                    type=summary_activity.get("type"),
                    start_date=self._parse_datetime(summary_activity["start_date"]),
                    distance=summary_activity.get("distance"),
                    moving_time=summary_activity.get("moving_time"),
                    elapsed_time=summary_activity.get("elapsed_time"),
                    elevation_gain=summary_activity.get("total_elevation_gain"),
                    description=summary_activity.get("description"),
                    polyline=self._extract_polyline(summary_activity),
                    timezone=summary_activity.get("timezone"),
                    location_country=summary_activity.get("location_country"),
                    raw_payload=summary_activity,
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

        while True:
            response = self.http_client.get(
                self.activity_list_url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
            if response.status_code == 429:
                self.sleep_fn(self._retry_after_seconds(response))
                continue
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise self._to_http_exception(exc) from exc
            break
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Invalid Strava activity list response")
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

    @staticmethod
    def _to_http_exception(exc: httpx.HTTPStatusError) -> HTTPException:
        status_code = exc.response.status_code
        if status_code >= 500:
            return HTTPException(status_code=502, detail="Strava API unavailable")
        return HTTPException(status_code=status_code, detail="Strava API error")

    @staticmethod
    def _retry_after_seconds(response: httpx.Response) -> int:
        retry_after = response.headers.get("Retry-After")
        if retry_after is None:
            return 60
        try:
            return max(int(retry_after), 1)
        except ValueError:
            return 60