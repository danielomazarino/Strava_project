from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.activities import router as activities_router
from app.api.auth import router as auth_router
from app.api.diary import router as diary_router
from app.api.health import router as health_router
from app.api.insights import router as insights_router
from app.api.heatmaps import router as heatmaps_router
from app.api.search import router as search_router
from app.core.config import get_cors_origins, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.bootstrap import initialize_database

settings = get_settings()
configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(_: FastAPI):
	initialize_database(settings.database_url)
	yield


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
app.include_router(auth_router)
app.include_router(diary_router)
app.include_router(health_router)
app.include_router(insights_router)
app.include_router(heatmaps_router)
app.include_router(search_router)
