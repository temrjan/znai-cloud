"""Celery application configuration."""
from celery import Celery

from backend.app.config import settings

# Create Celery app
celery_app = Celery(
    "ai_avangard",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.app.tasks.document_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completes
    task_reject_on_worker_lost=True,  # Requeue if worker dies

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour

    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_concurrency=2,  # 2 concurrent workers

    # Task time limits
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
)

# Task routes (optional - for future scaling)
celery_app.conf.task_routes = {
    "backend.app.tasks.document_tasks.*": {"queue": "documents"},
}
