from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import httpx

from app.core.config import Settings
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.schemas.insights import PatternInsight, RegionComparisonInsight, SummaryInsight


class LLMModelClient(Protocol):
    async def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class OllamaLLMModelClient:
    base_url: str
    model: str

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url.rstrip('/')}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
            )
            response.raise_for_status()
            return response.json()["response"]


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
        schema = (
            '{"summary": "2-3 sentence narrative of the training period", '
            '"volume": "low|moderate|high", '
            '"intensity": "low|moderate|high", '
            '"notable_events": ["event description"], '
            '"subjective_notes": ["note from athlete description"], '
            '"performance_patterns": ["observed pattern"]}'
        )
        lines = [
            "Summary Prompt",
            f"Analyze training activities between {start_date.date()} and {end_date.date()}.",
            "Return ONLY a JSON object matching this schema exactly:",
            schema,
            "Base your answer only on the activities listed. Do not invent data.",
            "Activities (date | name | type | description | country):",
        ]
        lines.extend(self._format_activity_lines(activities))
        return "\n".join(lines)

    def build_pattern_prompt(self, activities: list[Any]) -> str:
        schema = (
            '{"patterns": ["recurring pattern"], '
            '"fatigue": ["fatigue signal observed"], '
            '"motivation": ["motivation signal observed"], '
            '"terrain_effects": ["terrain effect on performance"], '
            '"weather_effects": ["weather effect on performance"], '
            '"pacing_issues": ["pacing issue observed"]}'
        )
        lines = [
            "Pattern Detection Prompt",
            "Analyze the training notes below and identify recurring patterns.",
            "Return ONLY a JSON object matching this schema exactly:",
            schema,
            "Use only the data provided. Do not invent data.",
            "Notes (date | description | country):",
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
        schema = (
            '{"region_a": "region name", '
            '"region_b": "region name", '
            '"perceived_effort": "easier|similar|harder", '
            '"terrain_differences": ["observed difference"], '
            '"pacing_differences": ["observed difference"], '
            '"subjective_notes": ["observation from athlete notes"]}'
        )
        lines = [
            "Region Comparison Prompt",
            f"Compare training in {region_a} vs {region_b}.",
            "Return ONLY a JSON object matching this schema exactly:",
            schema,
        ]
        if start_date is not None and end_date is not None:
            lines.append(f"Time window: {start_date.date()} to {end_date.date()}.")
        lines.extend(
            [
                "Use only the data provided. Do not invent data.",
                f"Activities in {region_a} (date | name | type | description | country):",
            ]
        )
        lines.extend(self._format_activity_lines(activities_a))
        lines.append(f"Activities in {region_b} (date | name | type | description | country):")
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
