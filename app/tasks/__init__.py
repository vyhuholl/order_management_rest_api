"""Celery application and task definitions."""

from celery import Celery

from app.core.config import settings

# Create Celery application
# Celery uses RabbitMQ as broker for its own task queue
celery_app = Celery(
    "ecommerce_tasks",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)

# Import tasks to register them with Celery
from app.tasks.order_tasks import process_order  # noqa: F401, E402
