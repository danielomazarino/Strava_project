from __future__ import annotations

from collections.abc import Generator
from urllib.parse import quote
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import Settings, get_cors_origins, get_settings, is_production_environment
from app.core.security import create_oauth_state, unpack_oauth_state
from app.db.bootstrap import DEV_DEMO_STRAVA_ATHLETE_ID
from app.db.repositories.activity_repo import ActivityRepository
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.services.oauth_service import OAuthService, build_authorize_url
from app.services.strava_import_service import StravaImportService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_http_client() -> Generator[httpx.Client, None, None]:
    client = httpx.Client(timeout=10.0)
    try:
        yield client
    finally:
        client.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def get_oauth_service(
    settings: Settings = Depends(get_settings),
    user_repository: UserRepository = Depends(get_user_repository),
    http_client: httpx.Client = Depends(get_http_client),
) -> OAuthService:
    return OAuthService(
        settings=settings,
        user_repository=user_repository,
        http_client=http_client,
    )


def get_strava_import_service(
    settings: Settings = Depends(get_settings),
    user_repository: UserRepository = Depends(get_user_repository),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
    http_client: httpx.Client = Depends(get_http_client),
) -> StravaImportService:
    return StravaImportService(
        settings=settings,
        user_repository=user_repository,
        activity_repository=activity_repository,
        http_client=http_client,
    )


def _build_dev_callback_url(request: Request, settings: Settings) -> str:
    referer = request.headers.get("referer")
    if referer:
        parsed = urlparse(referer)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}/auth/callback"

    cors_origins = get_cors_origins(settings)
    preferred_origins = [origin for origin in cors_origins if origin.endswith(":5173") or origin.endswith(":5174")]
    for origin in preferred_origins + cors_origins:
        if origin.startswith("http://") or origin.startswith("https://"):
            return f"{origin.rstrip('/')}/auth/callback"

    return "http://127.0.0.1:5173/auth/callback"


@router.get("/login", name="auth_login")
def login(request: Request, settings: Settings = Depends(get_settings)) -> RedirectResponse:
    state = create_oauth_state(settings.secret_key, return_to=_build_dev_callback_url(request, settings))
    if not settings.strava_client_id:
        if settings.environment.lower() not in {"production", "railway"}:
            return_to = quote(_build_dev_callback_url(request, settings), safe="")
            mock_login_url = request.url_for("auth_mock_login")
            return RedirectResponse(url=f"{mock_login_url}?return_to={return_to}", status_code=302)

        raise HTTPException(status_code=500, detail="STRAVA_CLIENT_ID is not configured")

    redirect_uri = str(request.url_for("auth_callback"))
    authorize_url = build_authorize_url(
        client_id=settings.strava_client_id,
        redirect_uri=redirect_uri,
        state=state,
    )
    return RedirectResponse(url=authorize_url, status_code=302)


@router.get("/mock-login", name="auth_mock_login")
def mock_login(
    return_to: str,
    settings: Settings = Depends(get_settings),
) -> RedirectResponse:
    if is_production_environment(settings) or not settings.enable_dev_mock_auth:
        raise HTTPException(status_code=404, detail="Not found")

    state = create_oauth_state(settings.secret_key)
    separator = "&" if "?" in return_to else "?"
    redirect_url = (
        f"{return_to}{separator}"
        f"code={quote(f'mock-{DEV_DEMO_STRAVA_ATHLETE_ID}')}&"
        f"state={quote(state)}"
    )
    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/callback", name="auth_callback")
def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    settings: Settings = Depends(get_settings),
    oauth_service: OAuthService = Depends(get_oauth_service),
    activity_repository: ActivityRepository = Depends(get_activity_repository),
    import_service: StravaImportService = Depends(get_strava_import_service),
) -> dict[str, object]:
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth callback parameters")

    user = oauth_service.complete_callback(
        code=code,
        state=state,
        redirect_uri=str(request.url_for("auth_callback")),
    )

    latest_start_date = activity_repository.get_latest_start_date_for_user(user_id=user.id)
    imported_count = import_service.import_activities(
        strava_athlete_id=user.strava_athlete_id,
        after=int(latest_start_date.timestamp()) if latest_start_date is not None else None,
    )

    return_to = unpack_oauth_state(state, settings.secret_key)
    accept_header = request.headers.get("accept", "")
    if return_to and "text/html" in accept_header:
        redirect_url = (
            f"{return_to}?"
            f"user_id={quote(str(user.id), safe='')}&"
            f"strava_athlete_id={quote(str(user.strava_athlete_id), safe='')}"
        )
        return RedirectResponse(url=redirect_url, status_code=302)

    return {
        "status": "connected",
        "user_id": str(user.id),
        "strava_athlete_id": user.strava_athlete_id,
        "imported_count": imported_count,
    }