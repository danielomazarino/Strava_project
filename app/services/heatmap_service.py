from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.heatmap import ActivityGeoData, GeoBounds, GeoPoint, HeatmapTile, HeatmapTilePoint


@dataclass(frozen=True)
class HeatmapService:
    user_repository: UserRepository
    activity_repository: ActivityRepository

    def decode_polyline(self, encoded: str) -> list[GeoPoint]:
        if not encoded:
            return []

        index = 0
        latitude = 0
        longitude = 0
        points: list[GeoPoint] = []

        while index < len(encoded):
            latitude_change, index = self._decode_value(encoded, index)
            longitude_change, index = self._decode_value(encoded, index)
            latitude += latitude_change
            longitude += longitude_change
            points.append(GeoPoint(lat=latitude / 1e5, lng=longitude / 1e5))

        return points

    def extract_geo_data(self, activity: Any) -> ActivityGeoData:
        points = self.decode_polyline(activity.polyline or "")
        return ActivityGeoData(
            activity_id=activity.id,
            strava_activity_id=activity.strava_activity_id,
            point_count=len(points),
            bounding_box=self._bounding_box(points),
            points=points,
        )

    def build_tile(
        self,
        *,
        strava_athlete_id: int,
        z: int,
        x: int,
        y: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        activity_type: str | None = None,
        country: str | None = None,
    ) -> HeatmapTile:
        user = self._get_user(strava_athlete_id)
        activities = self._filter_activities(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
            activity_type=activity_type,
            country=country,
        )

        tile_points: list[HeatmapTilePoint] = []
        activity_ids: set[str] = set()
        for activity in activities:
            geo_data = self.extract_geo_data(activity)
            for point in geo_data.points:
                if self._point_in_tile(point.lat, point.lng, z, x, y):
                    tile_points.append(
                        HeatmapTilePoint(
                            activity_id=activity.id,
                            strava_activity_id=activity.strava_activity_id,
                            lat=point.lat,
                            lng=point.lng,
                        )
                    )
                    activity_ids.add(str(activity.id))

        return HeatmapTile(
            z=z,
            x=x,
            y=y,
            point_count=len(tile_points),
            activity_count=len(activity_ids),
            bounds=self._tile_bounds(z, x, y),
            generated_at=datetime.now(timezone.utc),
            points=tile_points,
        )

    def _get_user(self, strava_athlete_id: int):
        user = self.user_repository.get_by_strava_athlete_id(strava_athlete_id)
        if user is None:
            raise ValueError("User not found")
        return user

    def _filter_activities(
        self,
        *,
        user_id,
        start_date: datetime | None,
        end_date: datetime | None,
        activity_type: str | None,
        country: str | None,
    ) -> list[Any]:
        activities = self.activity_repository.list_by_user_id(user_id=user_id)
        filtered: list[Any] = []
        for activity in activities:
            if start_date is not None and activity.start_date < start_date:
                continue
            if end_date is not None and activity.start_date > end_date:
                continue
            if activity_type is not None and (activity.type or "").lower() != activity_type.lower():
                continue
            if country is not None and (activity.location_country or "").lower() != country.lower():
                continue
            filtered.append(activity)
        return filtered

    @staticmethod
    def _decode_value(encoded: str, index: int) -> tuple[int, int]:
        result = 0
        shift = 0
        while True:
            if index >= len(encoded):
                raise ValueError("Invalid encoded polyline")
            value = ord(encoded[index]) - 63
            index += 1
            result |= (value & 0x1F) << shift
            shift += 5
            if value < 0x20:
                break
        delta = ~(result >> 1) if result & 1 else (result >> 1)
        return delta, index

    @staticmethod
    def _bounding_box(points: list[GeoPoint]) -> GeoBounds | None:
        if not points:
            return None
        latitudes = [point.lat for point in points]
        longitudes = [point.lng for point in points]
        return GeoBounds(
            min_lat=min(latitudes),
            min_lng=min(longitudes),
            max_lat=max(latitudes),
            max_lng=max(longitudes),
        )

    @staticmethod
    def _point_in_tile(lat: float, lng: float, z: int, x: int, y: int) -> bool:
        tile_x, tile_y = HeatmapService._lat_lng_to_tile(lat, lng, z)
        return tile_x == x and tile_y == y

    @staticmethod
    def _lat_lng_to_tile(lat: float, lng: float, z: int) -> tuple[int, int]:
        lat_rad = math.radians(lat)
        n = 2**z
        x = int((lng + 180.0) / 360.0 * n)
        y = int(
            (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi)
            / 2.0
            * n
        )
        return x, y

    @staticmethod
    def _tile_bounds(z: int, x: int, y: int) -> GeoBounds:
        n = 2**z
        west = x / n * 360.0 - 180.0
        east = (x + 1) / n * 360.0 - 180.0
        north = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        south = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
        return GeoBounds(min_lat=south, min_lng=west, max_lat=north, max_lng=east)
