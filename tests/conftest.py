"""Pytest fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Ensure all models are registered so create_all creates their tables
from app.models import Order, User  # noqa: F401

# In-memory SQLite for tests; StaticPool keeps one connection so tables are visible
SQLITE_TEST_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    """Yield a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """FastAPI test client with in-memory SQLite DB."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Register, login, and return Authorization header value."""
    client.post(
        "/register/",
        json={"email": "me@example.com", "password": "secret123"},
    )
    response = client.post(
        "/token/",
        data={"username": "me@example.com", "password": "secret123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
