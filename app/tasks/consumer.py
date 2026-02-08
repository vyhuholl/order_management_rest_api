"""RabbitMQ consumer that triggers Celery tasks."""

import json
import logging

import pika

from app.core.config import settings
from app.core.events import NEW_ORDER_QUEUE
from app.tasks.order_tasks import process_order


def callback(ch, method, properties, body):
    """Process incoming messages from new_order queue.

    Args:
        ch: Channel object
        method: Delivery method
        properties: Message properties
        body: Message body (JSON string)
    """
    try:
        # Parse message
        message = json.loads(body)
        order_id = message.get("order_id")
        # Trigger Celery task
        process_order.delay(order_id)
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception:
        logging.exception("Error processing order")
        # Reject and requeue the message on error
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """Start the RabbitMQ consumer.

    This function blocks and continuously listens for messages
    on the new_order queue.
    """
    try:
        # Connect to RabbitMQ
        params = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Declare queue (idempotent)
        channel.queue_declare(queue=NEW_ORDER_QUEUE, durable=True)

        # Set prefetch count (process one message at a time)
        channel.basic_qos(prefetch_count=1)

        # Subscribe to queue
        channel.basic_consume(
            queue=NEW_ORDER_QUEUE,
            on_message_callback=callback,
            auto_ack=False,  # Manual acknowledgment
        )

        # Start consuming (blocks)
        channel.start_consuming()
    except Exception:
        logging.exception("Consumer error")


if __name__ == "__main__":
    start_consumer()
