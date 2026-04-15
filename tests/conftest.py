from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_app.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, future=True
)

TestingSessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, future=True
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    test_db = Path("test_app.db")
    if test_db.exists():
        test_db.unlink()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
