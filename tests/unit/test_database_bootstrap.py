from __future__ import annotations

from sqlalchemy import create_engine, inspect

from app.db.bootstrap import initialize_database


def test_initialize_database_creates_tables(tmp_path):
    database_path = tmp_path / "bootstrap.sqlite3"
    database_url = f"sqlite:///{database_path}"

    initialize_database(database_url)

    engine = create_engine(database_url)
    inspector = inspect(engine)

    assert "users" in inspector.get_table_names()
    assert "activities" in inspector.get_table_names()