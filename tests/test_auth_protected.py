"""Tests for protected route access (JWT required)."""

import pytest


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


def test_protected_route_accepts_valid_token(client, auth_headers):
    """GET /users/me/ with valid Bearer token returns 200 and user."""
    response = client.get("/users/me/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert "id" in data


def test_protected_route_rejects_missing_token(client):
    """GET /users/me/ without Authorization returns 401."""
    response = client.get("/users/me/")
    assert response.status_code == 401


def test_protected_route_rejects_invalid_token(client):
    """GET /users/me/ with invalid JWT returns 401."""
    response = client.get(
        "/users/me/",
        headers={"Authorization": "Bearer invalid.jwt.here"},
    )
    assert response.status_code == 401
