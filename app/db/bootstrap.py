from __future__ import annotations

from sqlalchemy import create_engine

from app.db.base import Base

import app.db.models  # noqa: F401


def initialize_database(database_url: str) -> None:
    if not database_url:
        return

    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        Base.metadata.create_all(engine)
    finally:
        engine.dispose()