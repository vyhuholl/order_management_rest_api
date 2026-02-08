"""Order service: create, get by id (cache-first), update status, list by user."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.events import publish_new_order
from app.core.redis_client import (
    cache_order_delete,
    cache_order_get,
    cache_order_set,
)
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


def _order_to_dict(order: Order) -> dict[str, Any]:
    """Serialize Order to a dict for cache and API (created_at as ISO string)."""
    created = order.created_at
    if isinstance(created, datetime):
        created_str = created.isoformat()
    else:
        created_str = str(created) if created else None
    return {
        "id": order.id,
        "user_id": order.user_id,
        "items": order.items or [],
        "total_price": order.total_price,
        "status": str(order.status) if order.status else "PENDING",
        "created_at": created_str,
    }


def create_order(db: Session, user_id: int, data: OrderCreate) -> Order:
    """
    Create an order, publish new_order event, return the created order.
    """
    order = Order(
        user_id=user_id,
        items=data.items,
        total_price=data.total_price,
        status="PENDING",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    publish_new_order(order_id=order.id, user_id=order.user_id)
    return order


def get_order_by_id(
    db: Session, order_id: str, current_user_id: int
) -> dict[str, Any] | None:
    """
    Get order by id: cache-first (Redis then DB). Set cache on DB read.
    Return order dict only if order belongs to current_user_id; else None (404).
    """
    # Try cache first
    cached = cache_order_get(order_id)
    if cached is not None:
        if cached.get("user_id") != current_user_id:
            return None
        return cached
    # DB
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None or order.user_id != current_user_id:
        return None
    data = _order_to_dict(order)
    cache_order_set(order_id, data)
    return data


def update_order_status(
    db: Session, order_id: str, current_user_id: int, data: OrderUpdate
) -> Order | None:
    """
    Update order status only if order belongs to current user. Invalidate cache.
    Return updated Order or None (404).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None or order.user_id != current_user_id:
        return None
    if data.status is not None:
        order.status = data.status
    db.commit()
    db.refresh(order)
    cache_order_delete(order_id)
    return order


def list_orders_by_user(
    db: Session, user_id: int, current_user_id: int
) -> list[Order] | None:
    """
    List orders for user_id. Return list only if user_id == current_user_id;
    else return None (403).
    """
    if user_id != current_user_id:
        return None
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    return list(orders)
