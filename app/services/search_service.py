from __future__ import annotations

from dataclasses import dataclass

from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.search import SearchResult


@dataclass(frozen=True)
class SearchService:
    user_repository: UserRepository
    activity_repository: ActivityRepository

    def keyword_search(self, *, strava_athlete_id: int, query: str) -> list[SearchResult]:
        user = self._get_user(strava_athlete_id)
        activities = self.activity_repository.search_by_user_id(user_id=user.id, query=query)
        return [self._to_search_result(activity, score=1.0) for activity in activities]

    def semantic_search(self, *, strava_athlete_id: int, query: str, limit: int = 5) -> list[SearchResult]:
        user = self._get_user(strava_athlete_id)
        activities = self.activity_repository.list_by_user_id(user_id=user.id)
        scored = [
            (self._score_activity(activity, query), activity)
            for activity in activities
        ]
        scored = [item for item in scored if item[0] > 0]
        scored.sort(key=lambda item: (-item[0], item[1].start_date, str(item[1].id)))
        return [
            self._to_search_result(activity, score=score)
            for score, activity in scored[:limit]
        ]

    def _score_activity(self, activity, query: str) -> float:
        query_terms = {term for term in query.lower().split() if term}
        if not query_terms:
            return 0.0

        searchable_text = " ".join(
            str(part)
            for part in [
                activity.name or "",
                activity.type or "",
                activity.description or "",
                activity.location_country or "",
            ]
        ).lower()
        matches = sum(1 for term in query_terms if term in searchable_text)
        return matches / len(query_terms)

    def _get_user(self, strava_athlete_id: int):
        user = self.user_repository.get_by_strava_athlete_id(strava_athlete_id)
        if user is None:
            raise ValueError("User not found")
        return user

    @staticmethod
    def _to_search_result(activity, *, score: float) -> SearchResult:
        return SearchResult(
            id=activity.id,
            strava_activity_id=activity.strava_activity_id,
            name=activity.name,
            type=activity.type,
            start_date=activity.start_date,
            score=score,
        )
