from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.admin import get_activity_repository, get_user_repository
from app.core.config import get_settings
from app.main import app


class FakeUserRepository:
    def __init__(self):
        self.users = [
            SimpleNamespace(
                id=uuid4(),
                strava_athlete_id=111,
                token_expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            ),
            SimpleNamespace(
                id=uuid4(),
                strava_athlete_id=222,
                token_expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            ),
        ]

    def list_all_users(self):
        return self.users


class FakeActivityRepository:
    def __init__(self, user_repository: FakeUserRepository):
        self.user_repository = user_repository

    def list_by_user_id(self, *, user_id):
        if user_id == self.user_repository.users[0].id:
            return [
                SimpleNamespace(
                    id=uuid4(),
                    user_id=user_id,
                    strava_activity_id=5001,
                    name='Morning Run',
                    type='Run',
                    start_date=datetime(2026, 4, 7, 8, 0, tzinfo=timezone.utc),
                    distance=10_000,
                    moving_time=1_800,
                    elapsed_time=1_900,
                    elevation_gain=120,
                    description='Morning run summary',
                    polyline='polyline-a',
                    timezone='Europe/Stockholm',
                    location_country='GB',
                    raw_payload={'id': 5001},
                    created_at=datetime(2026, 4, 7, 8, 5, tzinfo=timezone.utc),
                    updated_at=datetime(2026, 4, 7, 8, 6, tzinfo=timezone.utc),
                ),
                SimpleNamespace(
                    id=uuid4(),
                    user_id=user_id,
                    strava_activity_id=5000,
                    name='Earlier Ride',
                    type='Ride',
                    start_date=datetime(2026, 4, 5, 8, 0, tzinfo=timezone.utc),
                    distance=20_000,
                    moving_time=3_600,
                    elapsed_time=3_700,
                    elevation_gain=240,
                    description='Steady road ride',
                    polyline='polyline-b',
                    timezone='Europe/Stockholm',
                    location_country='SE',
                    raw_payload=None,
                    created_at=datetime(2026, 4, 5, 8, 5, tzinfo=timezone.utc),
                    updated_at=datetime(2026, 4, 5, 8, 6, tzinfo=timezone.utc),
                ),
            ]

        return [
            SimpleNamespace(
                id=uuid4(),
                user_id=user_id,
                strava_activity_id=6000,
                name='Recovery Spin',
                type='Ride',
                start_date=datetime(2026, 4, 6, 8, 0, tzinfo=timezone.utc),
                distance=15_000,
                moving_time=2_400,
                elapsed_time=2_450,
                elevation_gain=80,
                description='Recovery spin after the weekend',
                polyline='polyline-c',
                timezone='Europe/Copenhagen',
                location_country='DK',
                raw_payload={'id': 6000},
                created_at=datetime(2026, 4, 6, 8, 5, tzinfo=timezone.utc),
                updated_at=datetime(2026, 4, 6, 8, 6, tzinfo=timezone.utc),
            )
        ]


def test_admin_overview_returns_read_only_summary():
    user_repository = FakeUserRepository()
    activity_repository = FakeActivityRepository(user_repository)
    app.dependency_overrides[get_user_repository] = lambda: user_repository
    app.dependency_overrides[get_activity_repository] = lambda: activity_repository
    client = TestClient(app)

    response = client.get('/admin/overview')

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['totals']['users'] == 2
    assert payload['totals']['activities'] == 3
    assert payload['totals']['active_tokens'] == 1
    assert payload['totals']['expired_tokens'] == 1
    assert payload['users'][0]['strava_athlete_id'] == 111
    assert payload['users'][0]['activity_count'] == 2
    assert payload['users'][1]['token_health'] == 'expired'
    assert payload['recent_activities'][0]['strava_activity_id'] == 5001
    assert payload['recent_activities'][0]['has_raw_payload'] is True
    assert payload['records'][0]['token_health'] == 'active'
    assert len(payload['records']) == 3


def test_admin_overview_is_hidden_in_production(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('STRAVA_CLIENT_ID', 'client-123')
    monkeypatch.setenv('STRAVA_CLIENT_SECRET', 'secret-456')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://user:pass@localhost/db')
    monkeypatch.setenv('SECRET_KEY', 'production-secret')
    monkeypatch.setenv('LLM_MODEL_PATH', '/models/gemma')
    monkeypatch.setenv('CORS_ORIGINS', 'https://example.com')

    client = TestClient(app)

    response = client.get('/admin/overview')

    get_settings.cache_clear()

    assert response.status_code == 404