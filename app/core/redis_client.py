"""Redis client for order cache (get/set/delete with TTL)."""

import json
from typing import Any

import redis

from app.core.config import settings

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Return a Redis client (sync). Creates one if not yet created."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


def order_cache_key(order_id: str) -> str:
    """Return Redis key for an order by id."""
    return f"order:{order_id}"


def cache_order_get(order_id: str) -> dict[str, Any] | None:
    """
    Get order from cache by id. Returns None on miss or error.
    """
    try:
        client = get_redis()
        key = order_cache_key(order_id)
        data = client.get(key)
        if data is None:
            return None
        return json.loads(data)
    except Exception:
        return None


def cache_order_set(order_id: str, order_data: dict[str, Any]) -> None:
    """
    Set order in cache with TTL (5 minutes). No-op on error.
    """
    try:
        client = get_redis()
        key = order_cache_key(order_id)
        ttl = getattr(settings, "CACHE_TTL", 300)
        client.setex(
            key,
            ttl,
            json.dumps(order_data, default=str),
        )
    except Exception:
        pass


def cache_order_delete(order_id: str) -> None:
    """
    Invalidate cache entry for an order. No-op on error.
    """
    try:
        client = get_redis()
        key = order_cache_key(order_id)
        client.delete(key)
    except Exception:
        pass
