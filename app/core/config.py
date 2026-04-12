from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from sqlalchemy.engine import make_url


@dataclass(frozen=True)
class Settings:
    strava_client_id: str = ""
    strava_client_secret: str = ""
    database_url: str = ""
    secret_key: str = ""
    llm_model_path: str = ""
    ollama_base_url: str = ""
    cors_origins: str = ""
    log_level: str = "INFO"
    environment: str = "development"
    enable_dev_mock_auth: bool = False


def _is_truthy_env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}


def is_production_environment(settings: Settings) -> bool:
    normalized_environment = settings.environment.lower()
    if normalized_environment in {"development", "dev", "test", "local"}:
        return False

    return normalized_environment in {"production", "railway"} or os.getenv("RAILWAY_ENVIRONMENT") == "production"


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

    if _is_truthy_env_flag("ENABLE_DEV_MOCK_AUTH"):
        raise ValueError("ENABLE_DEV_MOCK_AUTH must remain false in production")

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
    environment = os.getenv("APP_ENV", "development")
    normalized_environment = environment.lower()
    production_environment = normalized_environment not in {"development", "dev", "test", "local"} and (
        normalized_environment in {"production", "railway"} or os.getenv("RAILWAY_ENVIRONMENT") == "production"
    )
    raw_database_url = os.getenv("DATABASE_URL", "")
    raw_strava_client_id = os.getenv("STRAVA_CLIENT_ID", "")
    raw_secret_key = os.getenv("SECRET_KEY", "")
    raw_enable_dev_mock_auth = _is_truthy_env_flag("ENABLE_DEV_MOCK_AUTH")
    if raw_database_url:
        database_url = raw_database_url
    elif production_environment:
        database_url = ""
    else:
        database_path = Path(__file__).resolve().parents[2] / "strava_training_diary.sqlite3"
        database_url = f"sqlite:///{database_path}"

    settings = Settings(
        strava_client_id=raw_strava_client_id,
        strava_client_secret=os.getenv("STRAVA_CLIENT_SECRET", ""),
        database_url=database_url,
        secret_key=raw_secret_key or ("strava-training-diary-dev-secret" if not production_environment else ""),
        llm_model_path=os.getenv("LLM_MODEL_PATH", ""),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", ""),
        cors_origins=os.getenv("CORS_ORIGINS", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        environment=environment,
        enable_dev_mock_auth=raw_enable_dev_mock_auth or (not production_environment and not raw_strava_client_id),
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
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]