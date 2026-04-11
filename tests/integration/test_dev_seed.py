from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings
from app.db.bootstrap import DEV_DEMO_STRAVA_ATHLETE_ID, initialize_database, seed_development_database
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
import app.main as app_module


def test_seed_development_database_is_idempotent(tmp_path):
	database_url = f"sqlite:///{tmp_path / 'seed.sqlite3'}"
	initialize_database(database_url)
	seed_development_database(database_url, secret_key='seed-secret')
	seed_development_database(database_url, secret_key='seed-secret')

	engine = create_engine(database_url)
	session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
	session = session_factory()
	try:
		user_repository = UserRepository(session)
		activity_repository = ActivityRepository(session)
		user = user_repository.get_by_strava_athlete_id(DEV_DEMO_STRAVA_ATHLETE_ID)

		assert user is not None

		activities = activity_repository.list_by_user_id(user_id=user.id)
		assert len(activities) == 8
		assert activities[0].name == 'Recovery Run'
	finally:
		session.close()
		engine.dispose()


def test_seeded_dev_app_serves_admin_and_diary(tmp_path, monkeypatch):
	database_url = f"sqlite:///{tmp_path / 'smoke.sqlite3'}"
	settings = Settings(
		strava_client_id='client-id',
		strava_client_secret='client-secret',
		database_url=database_url,
		secret_key='smoke-secret',
		llm_model_path='/models/gemma',
		cors_origins='http://localhost:5173',
		log_level='INFO',
		environment='development',
		enable_dev_mock_auth=False,
	)

	monkeypatch.setenv('APP_ENV', 'development')
	monkeypatch.setenv('DATABASE_URL', database_url)
	monkeypatch.setenv('SECRET_KEY', 'smoke-secret')
	monkeypatch.setenv('STRAVA_CLIENT_ID', 'client-id')
	monkeypatch.setenv('STRAVA_CLIENT_SECRET', 'client-secret')
	monkeypatch.setenv('LLM_MODEL_PATH', '/models/gemma')
	monkeypatch.setenv('CORS_ORIGINS', 'http://localhost:5173')
	monkeypatch.setattr(app_module, 'settings', settings)
	get_settings.cache_clear()

	with TestClient(app_module.app) as client:
		admin_response = client.get('/admin/overview')
		diary_response = client.get(f'/diary?strava_athlete_id={DEV_DEMO_STRAVA_ATHLETE_ID}')

	get_settings.cache_clear()

	assert admin_response.status_code == 200
	assert admin_response.json()['totals']['users'] == 1
	assert admin_response.json()['totals']['activities'] == 8
	assert len(admin_response.json()['records']) == 8

	assert diary_response.status_code == 200
	assert len(diary_response.json()['entries']) == 8
	assert diary_response.json()['entries'][0]['name'] == 'Recovery Run'