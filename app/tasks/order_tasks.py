"""Order processing tasks."""

import time

from app.tasks import celery_app


@celery_app.task(name="tasks.process_order")
def process_order(order_id: str) -> None:
    """Process an order asynchronously.

    Args:
        order_id: UUID of the order to process.

    This task simulates order processing by waiting 2 seconds
    and then logging a confirmation message.
    """
    time.sleep(2)
    print(f"Order {order_id} processed")  # noqa: T201
