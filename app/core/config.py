from dataclasses import dataclass
from functools import lru_cache
import os

from sqlalchemy.engine import make_url


@dataclass(frozen=True)
class Settings:
    strava_client_id: str = ""
    strava_client_secret: str = ""
    database_url: str = ""
    secret_key: str = ""
    llm_model_path: str = ""
    cors_origins: str = ""
    log_level: str = "INFO"
    environment: str = "development"


def is_production_environment(settings: Settings) -> bool:
    return settings.environment.lower() in {"production", "railway"} or os.getenv("RAILWAY_ENVIRONMENT") == "production"


def validate_database_url(settings: Settings) -> None:
    if not settings.database_url:
        return

    if not is_production_environment(settings):
        return

    url = make_url(settings.database_url)
    if url.drivername not in {"postgresql", "postgresql+psycopg2", "postgres"}:
        raise ValueError("Railway deployments must use PostgreSQL for DATABASE_URL")


def validate_production_settings(settings: Settings) -> None:
    if not is_production_environment(settings):
        return

    required_fields = {
        "STRAVA_CLIENT_ID": settings.strava_client_id,
        "STRAVA_CLIENT_SECRET": settings.strava_client_secret,
        "DATABASE_URL": settings.database_url,
        "SECRET_KEY": settings.secret_key,
        "LLM_MODEL_PATH": settings.llm_model_path,
        "CORS_ORIGINS": settings.cors_origins,
    }
    missing_fields = [name for name, value in required_fields.items() if not value]
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"Missing required production settings: {missing}")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings(
        strava_client_id=os.getenv("STRAVA_CLIENT_ID", ""),
        strava_client_secret=os.getenv("STRAVA_CLIENT_SECRET", ""),
        database_url=os.getenv("DATABASE_URL", ""),
        secret_key=os.getenv("SECRET_KEY", ""),
        llm_model_path=os.getenv("LLM_MODEL_PATH", ""),
        cors_origins=os.getenv("CORS_ORIGINS", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        environment=os.getenv("APP_ENV", "development"),
    )
    validate_database_url(settings)
    validate_production_settings(settings)
    return settings


def get_cors_origins(settings: Settings) -> list[str]:
    if settings.cors_origins:
        return [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

    if is_production_environment(settings):
        return []

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]