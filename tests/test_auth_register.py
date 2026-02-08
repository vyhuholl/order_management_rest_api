"""Tests for POST /register/ (registration)."""


def test_register_success(client):
    """Registration with valid email and password returns 201 and user (id, email)."""
    response = client.post(
        "/register/",
        json={"email": "user@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "user@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_returns_409(client):
    """Registration with an email that already exists returns 409."""
    payload = {"email": "dup@example.com", "password": "pass123"}
    client.post("/register/", json=payload)
    response = client.post("/register/", json=payload)
    assert response.status_code == 409
    assert "already" in response.json().get("detail", "").lower()
