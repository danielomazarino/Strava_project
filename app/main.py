from contextlib import asynccontextmanager
from threading import Event, Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.activities import router as activities_router
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.diary import router as diary_router
from app.api.health import router as health_router
from app.api.insights import router as insights_router
from app.api.heatmaps import router as heatmaps_router
from app.api.search import router as search_router
from app.core.config import get_cors_origins, get_settings, is_production_environment
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.bootstrap import initialize_database, seed_development_database
from app.workers.background_sync import start_background_sync

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
	initialize_database(settings.database_url)
	if not is_production_environment(settings):
		seed_development_database(settings.database_url, secret_key=settings.secret_key)

	background_sync_thread: Thread | None = None
	background_sync_stop_event: Event | None = None
	if is_production_environment(settings):
		background_sync_thread, background_sync_stop_event = start_background_sync(settings=settings)

	try:
		yield
	finally:
		if background_sync_stop_event is not None:
			background_sync_stop_event.set()
		if background_sync_thread is not None:
			background_sync_thread.join(timeout=5)


app = FastAPI(title="Strava Training Diary", lifespan=lifespan)

register_exception_handlers(app)

cors_origins = get_cors_origins(settings)
if cors_origins:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=cors_origins,
		allow_credentials=True,
		allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
		allow_headers=["Authorization", "Content-Type"],
	)

app.include_router(activities_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(diary_router)
app.include_router(health_router)
app.include_router(insights_router)
app.include_router(heatmaps_router)
app.include_router(search_router)
