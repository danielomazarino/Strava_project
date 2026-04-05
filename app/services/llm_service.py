from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from app.core.config import Settings
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.insights import PatternInsight, RegionComparisonInsight, SummaryInsight


class LLMModelClient(Protocol):
    async def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class StubLLMModelClient:
    async def generate(self, prompt: str) -> str:
        if prompt.startswith("Summary Prompt"):
            return json.dumps(
                {
                    "summary": "Stub summary",
                    "volume": "moderate",
                    "intensity": "moderate",
                    "notable_events": ["Stub notable event"],
                    "subjective_notes": ["Stub note"],
                    "performance_patterns": ["Stub pattern"],
                }
            )
        if prompt.startswith("Pattern Detection Prompt"):
            return json.dumps(
                {
                    "patterns": ["Stub pattern"],
                    "fatigue": ["Stub fatigue"],
                    "motivation": ["Stub motivation"],
                    "terrain_effects": ["Stub terrain"],
                    "weather_effects": ["Stub weather"],
                    "pacing_issues": ["Stub pacing"],
                }
            )
        if prompt.startswith("Region Comparison Prompt"):
            return json.dumps(
                {
                    "region_a": "Region A",
                    "region_b": "Region B",
                    "perceived_effort": "similar",
                    "terrain_differences": ["Stub terrain difference"],
                    "pacing_differences": ["Stub pacing difference"],
                    "subjective_notes": ["Stub comparison note"],
                }
            )
        return json.dumps({"response": "Stub response"})


@dataclass(frozen=True)
class LLMService:
    settings: Settings
    user_repository: UserRepository
    activity_repository: ActivityRepository
    model_client: LLMModelClient

    async def summarize_period(
        self,
        *,
        strava_athlete_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> SummaryInsight:
        user = self._get_user(strava_athlete_id)
        activities = self.activity_repository.list_by_user_id_between_dates(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
        )
        prompt = self.build_summary_prompt(
            start_date=start_date,
            end_date=end_date,
            activities=activities,
        )
        response = await self.model_client.generate(prompt)
        return SummaryInsight.model_validate(self._parse_response(response))

    async def detect_patterns(
        self,
        *,
        strava_athlete_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> PatternInsight:
        user = self._get_user(strava_athlete_id)
        activities = self.activity_repository.list_by_user_id_between_dates(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
        )
        prompt = self.build_pattern_prompt(activities)
        response = await self.model_client.generate(prompt)
        return PatternInsight.model_validate(self._parse_response(response))

    async def compare_regions(
        self,
        *,
        strava_athlete_id: int,
        region_a: str,
        region_b: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> RegionComparisonInsight:
        user = self._get_user(strava_athlete_id)
        activities_a = self.activity_repository.list_by_user_id_and_country(
            user_id=user.id,
            country=region_a,
            start_date=start_date,
            end_date=end_date,
        )
        activities_b = self.activity_repository.list_by_user_id_and_country(
            user_id=user.id,
            country=region_b,
            start_date=start_date,
            end_date=end_date,
        )
        prompt = self.build_region_comparison_prompt(
            region_a=region_a,
            region_b=region_b,
            activities_a=activities_a,
            activities_b=activities_b,
            start_date=start_date,
            end_date=end_date,
        )
        response = await self.model_client.generate(prompt)
        return RegionComparisonInsight.model_validate(self._parse_response(response))

    def build_summary_prompt(
        self,
        *,
        start_date: datetime,
        end_date: datetime,
        activities: list[Any],
    ) -> str:
        lines = [
            "Summary Prompt",
            f"Summarize the user's training between {start_date.isoformat()} and {end_date.isoformat()}.",
            "Focus on:",
            "volume",
            "intensity",
            "notable events",
            "subjective notes",
            "patterns in performance",
            "Do not invent data.",
            "Activities:",
        ]
        lines.extend(self._format_activity_lines(activities))
        return "\n".join(lines)

    def build_pattern_prompt(self, activities: list[Any]) -> str:
        lines = [
            "Pattern Detection Prompt",
            "Analyze the following training notes and identify recurring patterns.",
            "Focus on:",
            "fatigue",
            "motivation",
            "terrain effects",
            "weather effects",
            "pacing issues",
            "Do not add new interpretations.",
            "Notes:",
        ]
        lines.extend(self._format_note_lines(activities))
        return "\n".join(lines)

    def build_region_comparison_prompt(
        self,
        *,
        region_a: str,
        region_b: str,
        activities_a: list[Any],
        activities_b: list[Any],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> str:
        lines = [
            "Region Comparison Prompt",
            f"Compare the user's training experiences between {region_a} and {region_b}.",
        ]
        if start_date is not None and end_date is not None:
            lines.append(f"Time window: {start_date.isoformat()} to {end_date.isoformat()}.")
        lines.extend(
            [
                "Focus on:",
                "perceived effort",
                "terrain differences",
                "pacing differences",
                "subjective notes",
                "Do not invent data.",
                f"Region {region_a} activities:",
            ]
        )
        lines.extend(self._format_activity_lines(activities_a))
        lines.append(f"Region {region_b} activities:")
        lines.extend(self._format_activity_lines(activities_b))
        return "\n".join(lines)

    def _get_user(self, strava_athlete_id: int):
        user = self.user_repository.get_by_strava_athlete_id(strava_athlete_id)
        if user is None:
            raise ValueError("User not found")
        return user

    @staticmethod
    def _format_activity_lines(activities: list[Any]) -> list[str]:
        lines: list[str] = []
        for activity in sorted(activities, key=lambda item: (item.start_date, str(item.id))):
            lines.append(
                " | ".join(
                    [
                        str(activity.start_date.isoformat()),
                        str(activity.name or ""),
                        str(activity.type or ""),
                        str(activity.description or ""),
                        str(activity.location_country or ""),
                    ]
                )
            )
        if not lines:
            lines.append("No activities found.")
        return lines

    @staticmethod
    def _format_note_lines(activities: list[Any]) -> list[str]:
        lines: list[str] = []
        for activity in sorted(activities, key=lambda item: (item.start_date, str(item.id))):
            note = activity.description or activity.name or ""
            lines.append(f"{activity.start_date.isoformat()} | {note} | {activity.location_country or ''}")
        if not lines:
            lines.append("No notes found.")
        return lines

    @staticmethod
    def _parse_response(response: str) -> dict[str, Any]:
        payload = json.loads(response)
        if not isinstance(payload, dict):
            raise ValueError("LLM response must be a JSON object")
        return payload
