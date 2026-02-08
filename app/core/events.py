"""Event publishing (e.g. RabbitMQ new_order) for order lifecycle."""

import json

import pika

from app.core.config import settings

# Queue name for order-related tasks (consumed by Celery or other workers).
NEW_ORDER_QUEUE = "new_order"

# Payload shape for new_order event:
#   {"order_id": "<uuid string>", "user_id": <int>}


def publish_new_order(order_id: str, user_id: int) -> None:
    """
    Publish a new_order event to the configured RabbitMQ queue.
    Payload: {"order_id": "<str>", "user_id": <int>}.
    No-op on connection/publish errors (caller can log).
    """
    try:
        params = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=NEW_ORDER_QUEUE, durable=True)
        body = json.dumps({"order_id": order_id, "user_id": user_id})
        channel.basic_publish(
            exchange="",
            routing_key=NEW_ORDER_QUEUE,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
    except Exception:
        pass
