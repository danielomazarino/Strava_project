from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.config import Settings
from app.services.llm_service import LLMService


@dataclass
class FakeActivity:
    id: object
    strava_activity_id: int
    name: str
    type: str
    start_date: datetime
    description: str
    location_country: str


class FakeUserRepository:
    def get_by_strava_athlete_id(self, strava_athlete_id: int):
        return SimpleNamespace(id=uuid4(), strava_athlete_id=strava_athlete_id)


class FakeActivityRepository:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def list_by_user_id_between_dates(self, *, user_id, start_date, end_date):
        self.calls.append(("between", {"user_id": user_id, "start_date": start_date, "end_date": end_date}))
        return [
            FakeActivity(
                id=uuid4(),
                strava_activity_id=1,
                name="Tempo Run",
                type="Run",
                start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
                description="Hard tempo in windy weather",
                location_country="GB",
            )
        ]

    def list_by_user_id_and_country(self, *, user_id, country, start_date=None, end_date=None):
        self.calls.append(
            (
                "country",
                {
                    "user_id": user_id,
                    "country": country,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
        )
        if country == "GB":
            return [
                FakeActivity(
                    id=uuid4(),
                    strava_activity_id=2,
                    name="Hill Session",
                    type="Run",
                    start_date=datetime(2026, 4, 6, 8, 0, tzinfo=timezone.utc),
                    description="Hill repeats",
                    location_country="GB",
                )
            ]
        return []


class FakeModelClient:
    def __init__(self):
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if prompt.startswith("Summary Prompt"):
            return '{"summary":"Solid week","volume":"high","intensity":"moderate","notable_events":["Tempo run"],"subjective_notes":["Windy"],"performance_patterns":["Handled effort well"]}'
        if prompt.startswith("Pattern Detection Prompt"):
            return '{"patterns":["Recurring fatigue late week"],"fatigue":["Late week fatigue"],"motivation":["Motivation stayed stable"],"terrain_effects":["Hills increased load"],"weather_effects":["Wind made pace harder"],"pacing_issues":["Started too fast"]}'
        return '{"region_a":"GB","region_b":"FR","perceived_effort":"higher in GB","terrain_differences":["GB hills were harder"],"pacing_differences":["FR was steadier"],"subjective_notes":["Liked both"]}'


@pytest.fixture()
def llm_service():
    return LLMService(
        settings=Settings(secret_key="unit-test-secret"),
        user_repository=FakeUserRepository(),
        activity_repository=FakeActivityRepository(),
        model_client=FakeModelClient(),
    )


def test_summary_prompt_is_deterministic(llm_service):
    prompt = llm_service.build_summary_prompt(
        start_date=datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 4, 7, 0, 0, tzinfo=timezone.utc),
        activities=llm_service.activity_repository.list_by_user_id_between_dates(
            user_id=uuid4(),
            start_date=datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
            end_date=datetime(2026, 4, 7, 0, 0, tzinfo=timezone.utc),
        ),
    )

    assert prompt.startswith("Summary Prompt")
    assert "volume" in prompt
    assert "Tempo Run" in prompt


def test_summarize_period_parses_model_response(llm_service):
    analysis = asyncio.run(llm_service.summarize_period(
        strava_athlete_id=123,
        start_date=datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 4, 7, 0, 0, tzinfo=timezone.utc),
    ))

    assert analysis.summary == "Solid week"
    assert analysis.notable_events == ["Tempo run"]


def test_detect_patterns_parses_model_response(llm_service):
    analysis = asyncio.run(llm_service.detect_patterns(
        strava_athlete_id=123,
        start_date=datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 4, 7, 0, 0, tzinfo=timezone.utc),
    ))

    assert analysis.patterns == ["Recurring fatigue late week"]
    assert analysis.weather_effects == ["Wind made pace harder"]


def test_compare_regions_parses_model_response(llm_service):
    analysis = asyncio.run(llm_service.compare_regions(
        strava_athlete_id=123,
        region_a="GB",
        region_b="FR",
    ))

    assert analysis.region_a == "GB"
    assert analysis.region_b == "FR"
    assert analysis.perceived_effort == "higher in GB"
