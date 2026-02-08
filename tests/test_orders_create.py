"""Tests for POST /orders/ (order creation)."""


def test_create_order_success(client, auth_headers):
    """Create order with valid JWT and body returns 201 and order representation."""
    response = client.post(
        "/orders/",
        headers=auth_headers,
        json={"items": [{"name": "Widget", "qty": 2}], "total_price": 29.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == 1
    assert data["items"] == [{"name": "Widget", "qty": 2}]
    assert data["total_price"] == 29.99
    assert data["status"] == "PENDING"
    assert "created_at" in data


def test_create_order_unauthenticated_returns_401(client):
    """POST /orders/ without valid JWT returns 401."""
    response = client.post(
        "/orders/",
        json={"items": [], "total_price": 10.0},
    )
    assert response.status_code == 401
