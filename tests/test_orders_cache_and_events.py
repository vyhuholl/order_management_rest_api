"""Tests for cache invalidation on update and new_order event publish on create."""

from unittest.mock import patch


def test_new_order_event_published_on_create(client, auth_headers):
    """When order is successfully created, publish_new_order is called with order id and user_id."""
    with patch(
        "app.services.order_service.publish_new_order",
    ) as mock_publish:
        response = client.post(
            "/orders/",
            headers=auth_headers,
            json={"items": [{"a": 1}], "total_price": 12.0},
        )
        assert response.status_code == 201
        data = response.json()
        mock_publish.assert_called_once_with(
            order_id=data["id"],
            user_id=1,
        )


def test_cache_invalidated_on_patch(client, auth_headers):
    """When order is updated via PATCH, cache delete is called for that order id."""
    with patch(
        "app.services.order_service.cache_order_delete",
    ) as mock_delete:
        r = client.post(
            "/orders/",
            headers=auth_headers,
            json={"items": [], "total_price": 1.0},
        )
        assert r.status_code == 201
        order_id = r.json()["id"]
        client.patch(
            f"/orders/{order_id}",
            headers=auth_headers,
            json={"status": "PAID"},
        )
        mock_delete.assert_called_once_with(order_id)
