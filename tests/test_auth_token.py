"""Tests for POST /token/ (OAuth2 password flow login)."""

import base64
import json
import pytest


@pytest.fixture
def registered_user(client):
    """Register a user and return email and password."""
    client.post(
        "/register/",
        json={"email": "login@example.com", "password": "mypassword"},
    )
    return {"email": "login@example.com", "password": "mypassword"}


def test_token_success(client, registered_user):
    """Valid credentials return 200 with access_token and token_type bearer."""
    response = client.post(
        "/token/",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_token_jwt_has_sub_and_exp(client, registered_user):
    """Issued JWT contains sub (user id) and exp claims."""
    response = client.post(
        "/token/",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    # JWT format: header.payload.signature (payload is base64url)
    parts = token.split(".")
    assert len(parts) == 3
    payload_b64 = parts[1]
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding
    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    assert "sub" in payload
    assert "exp" in payload


def test_token_invalid_password_returns_401(client, registered_user):
    """Wrong password returns 401."""
    response = client.post(
        "/token/",
        data={
            "username": registered_user["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_token_invalid_email_returns_401(client):
    """Unknown email returns 401."""
    response = client.post(
        "/token/",
        data={"username": "nonexistent@example.com", "password": "any"},
    )
    assert response.status_code == 401
