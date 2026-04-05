from app.core.config import get_settings
from app.db.session import get_engine, get_session_factory


def test_get_engine_uses_configured_database_url(monkeypatch, tmp_path):
    get_settings.cache_clear()
    database_path = tmp_path / "session.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")

    engine = get_engine()

    assert str(engine.url).startswith("sqlite:///")


def test_get_session_factory_returns_sessionmaker(monkeypatch, tmp_path):
    get_settings.cache_clear()
    database_path = tmp_path / "session.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")

    session_factory = get_session_factory()

    assert session_factory.kw["autocommit"] is False
    assert session_factory.kw["autoflush"] is False