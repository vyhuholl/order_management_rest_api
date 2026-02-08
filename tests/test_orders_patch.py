"""Tests for PATCH /orders/{order_id} (update order status)."""

import pytest


@pytest.fixture
def order_id(client, auth_headers):
    """Create an order and return its id."""
    r = client.post(
        "/orders/",
        headers=auth_headers,
        json={"items": [], "total_price": 99.0},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_patch_order_success(client, auth_headers, order_id):
    """PATCH own order with valid status returns 200 and updated order."""
    response = client.patch(
        f"/orders/{order_id}",
        headers=auth_headers,
        json={"status": "PAID"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PAID"


def test_patch_order_other_user_returns_404(client, auth_headers, order_id):
    """PATCH order that belongs to another user returns 404."""
    client.post(
        "/register/",
        json={"email": "other2@example.com", "password": "other123"},
    )
    r = client.post(
        "/token/",
        data={"username": "other2@example.com", "password": "other123"},
    )
    other_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    response = client.patch(
        f"/orders/{order_id}",
        headers=other_headers,
        json={"status": "SHIPPED"},
    )
    assert response.status_code == 404


def test_patch_order_unauthenticated_returns_401(client, order_id):
    """PATCH without JWT returns 401."""
    response = client.patch(
        f"/orders/{order_id}",
        json={"status": "CANCELED"},
    )
    assert response.status_code == 401
