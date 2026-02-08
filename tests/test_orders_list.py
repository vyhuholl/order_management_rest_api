"""Tests for GET /orders/user/{user_id} (list orders by user)."""


def test_list_orders_own_user(client, auth_headers):
    """GET orders for current user returns 200 and list (path user_id matches token)."""
    client.post(
        "/orders/",
        headers=auth_headers,
        json={"items": [{"x": 1}], "total_price": 5.0},
    )
    response = client.get("/orders/user/1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["user_id"] == 1


def test_list_orders_other_user_returns_403(client, auth_headers):
    """GET orders for another user_id returns 403."""
    response = client.get("/orders/user/999", headers=auth_headers)
    assert response.status_code == 403


def test_list_orders_unauthenticated_returns_401(client):
    """GET /orders/user/1 without JWT returns 401."""
    response = client.get("/orders/user/1")
    assert response.status_code == 401
