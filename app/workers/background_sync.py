from __future__ import annotations

import logging
from threading import Event, Thread

import httpx

from app.core.config import Settings
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_session_factory
from app.services.oauth_service import OAuthService
from app.services.strava_import_service import StravaImportService
from app.workers.sync_worker import SyncResult, SyncWorker

logger = logging.getLogger(__name__)


def build_sync_worker(*, settings: Settings, session, http_client: httpx.Client) -> SyncWorker:
    user_repository = UserRepository(session)
    activity_repository = ActivityRepository(session)
    oauth_service = OAuthService(
        settings=settings,
        user_repository=user_repository,
        http_client=http_client,
    )
    import_service = StravaImportService(
        settings=settings,
        user_repository=user_repository,
        activity_repository=activity_repository,
        http_client=http_client,
    )
    return SyncWorker(
        settings=settings,
        user_repository=user_repository,
        activity_repository=activity_repository,
        oauth_service=oauth_service,
        import_service=import_service,
    )


def run_sync_cycle(*, settings: Settings, http_client: httpx.Client) -> list[SyncResult]:
    session_factory = get_session_factory()
    session = session_factory()
    try:
        worker = build_sync_worker(settings=settings, session=session, http_client=http_client)
        results = worker.run_once()
        if results:
            logger.info("Background sync completed for %s athlete(s)", len(results))
        return results
    finally:
        session.close()


def run_background_sync_loop(
    *,
    settings: Settings,
    stop_event: Event,
    interval_seconds: int = 300,
) -> None:
    with httpx.Client(timeout=20.0) as http_client:
        while not stop_event.is_set():
            try:
                run_sync_cycle(settings=settings, http_client=http_client)
            except Exception:
                logger.exception("Background sync cycle failed")

            if stop_event.wait(interval_seconds):
                break


def start_background_sync(
    *,
    settings: Settings,
    interval_seconds: int = 300,
) -> tuple[Thread, Event]:
    stop_event = Event()
    thread = Thread(
        target=run_background_sync_loop,
        kwargs={
            "settings": settings,
            "stop_event": stop_event,
            "interval_seconds": interval_seconds,
        },
        name="strava-background-sync",
        daemon=True,
    )
    thread.start()
    return thread, stop_event