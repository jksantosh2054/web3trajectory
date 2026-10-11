"""Celery application: outbox dispatch, scheduled maintenance tasks."""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "nexus",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "expire-presence-every-minute": {
            "task": "app.worker.tasks.expire_presence",
            "schedule": 60.0,
        },
        "close-auctions-every-minute": {
            "task": "app.worker.tasks.close_auctions",
            "schedule": 60.0,
        },
        "release-reservations-every-5-min": {
            "task": "app.worker.tasks.release_reservations",
            "schedule": 300.0,
        },
        "aggregate-engagement-hourly": {
            "task": "app.worker.tasks.aggregate_engagement",
            "schedule": 3600.0,
        },
    },
)
