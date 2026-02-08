"""Tests for GET /orders/{order_id} (get order by id, cache-first)."""

import pytest


@pytest.fixture
def order_id(client, auth_headers):
    """Create an order and return its id."""
    r = client.post(
        "/orders/",
        headers=auth_headers,
        json={"items": [{"sku": "A1"}], "total_price": 15.0},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_get_order_own_returns_200(client, auth_headers, order_id):
    """GET own order by id returns 200 and order (cache miss then DB)."""
    response = client.get(f"/orders/{order_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["total_price"] == 15.0


def test_get_order_other_user_returns_404(client, auth_headers, order_id):
    """GET order by id that belongs to another user returns 404."""
    client.post(
        "/register/",
        json={"email": "other@example.com", "password": "other123"},
    )
    r = client.post(
        "/token/",
        data={"username": "other@example.com", "password": "other123"},
    )
    other_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    response = client.get(f"/orders/{order_id}", headers=other_headers)
    assert response.status_code == 404


def test_get_order_nonexistent_returns_404(client, auth_headers):
    """GET non-existent order id returns 404."""
    response = client.get(
        "/orders/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_order_unauthenticated_returns_401(client, order_id):
    """GET /orders/{id} without JWT returns 401."""
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 401
