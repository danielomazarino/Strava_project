from __future__ import annotations

from collections.abc import Generator

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import create_oauth_state
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.services.oauth_service import OAuthService, build_authorize_url

router = APIRouter(prefix="/auth", tags=["auth"])


def get_http_client() -> Generator[httpx.Client, None, None]:
    client = httpx.Client(timeout=10.0)
    try:
        yield client
    finally:
        client.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


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


@router.get("/login", name="auth_login")
def login(request: Request, settings: Settings = Depends(get_settings)) -> RedirectResponse:
    state = create_oauth_state(settings.secret_key)
    redirect_uri = str(request.url_for("auth_callback"))
    authorize_url = build_authorize_url(
        client_id=settings.strava_client_id,
        redirect_uri=redirect_uri,
        state=state,
    )
    return RedirectResponse(url=authorize_url, status_code=302)


@router.get("/callback", name="auth_callback")
def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    oauth_service: OAuthService = Depends(get_oauth_service),
) -> dict[str, object]:
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth callback parameters")

    user = oauth_service.complete_callback(
        code=code,
        state=state,
        redirect_uri=str(request.url_for("auth_callback")),
    )
    return {
        "status": "connected",
        "user_id": str(user.id),
        "strava_athlete_id": user.strava_athlete_id,
    }