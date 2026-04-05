from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models.activity import Activity
from app.db.models.user import User


@pytest.fixture()
def sqlite_engine(tmp_path):
    database_path = tmp_path / "integration.sqlite3"
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture()
def sqlite_session(sqlite_engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()