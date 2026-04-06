from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import TOKEN_ENCRYPTION_VERSION, encrypt_secret
from app.db.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_strava_athlete_id(self, strava_athlete_id: int) -> User | None:
        statement = select(User).where(User.strava_athlete_id == strava_athlete_id)
        return self.session.execute(statement).scalars().one_or_none()

    def list_all_users(self) -> list[User]:
        statement = select(User).order_by(User.strava_athlete_id.asc())
        return list(self.session.execute(statement).scalars().all())

    def upsert_tokens(
        self,
        *,
        strava_athlete_id: int,
        access_token: str,
        refresh_token: str,
        token_expires_at: datetime,
        secret_key: str,
    ) -> User:
        user = self.get_by_strava_athlete_id(strava_athlete_id)
        encrypted_access_token = encrypt_secret(access_token, secret_key)
        encrypted_refresh_token = encrypt_secret(refresh_token, secret_key)

        if user is None:
            user = User(
                strava_athlete_id=strava_athlete_id,
                access_token_encrypted=encrypted_access_token,
                refresh_token_encrypted=encrypted_refresh_token,
                token_expires_at=token_expires_at,
                token_encryption_version=TOKEN_ENCRYPTION_VERSION,
            )
            self.session.add(user)
        else:
            user.access_token_encrypted = encrypted_access_token
            user.refresh_token_encrypted = encrypted_refresh_token
            user.token_expires_at = token_expires_at
            user.token_encryption_version = TOKEN_ENCRYPTION_VERSION

        self.session.flush()
        self.session.commit()
        return user