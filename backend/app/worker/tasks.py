"""Background tasks. All must be idempotent (at-least-once delivery)."""
from __future__ import annotations

from app.worker.celery_app import celery_app


@celery_app.task(name="app.worker.tasks.dispatch_outbox")
def dispatch_outbox() -> int:
    """Publish unpublished outbox_events rows to Redis Streams.

    Marks published_at only after broker ack. Idempotent via event ids.
    """
    # TODO: SELECT ... WHERE published_at IS NULL ORDER BY created_at LIMIT N
    #       FOR UPDATE SKIP LOCKED; publish; UPDATE published_at.
    return 0


@celery_app.task(name="app.worker.tasks.expire_presence")
def expire_presence() -> int:
    """Expire date_presence rows past expires_at (short TTL privacy rule)."""
    # TODO: UPDATE date_presence SET status='inactive' WHERE expires_at < now();
    #       optionally hard-delete after grace period.
    return 0


@celery_app.task(name="app.worker.tasks.close_auctions")
def close_auctions() -> int:
    """Close live auctions past ends_at (with anti-snipe extension), then settle."""
    # TODO: for each live & past-due auction: extend if last-bid within
    # anti_snipe_minutes, else move to closing and trigger settlement task.
    return 0


@celery_app.task(name="app.worker.tasks.release_reservations")
def release_reservations() -> int:
    """Release expired inventory_reservations for unpaid orders."""
    # TODO: DELETE reservations WHERE expires_at < now() AND order unpaid.
    return 0


@celery_app.task(name="app.worker.tasks.aggregate_engagement")
def aggregate_engagement() -> int:
    """Roll up engagement_events → hourly/daily aggregates (privacy-gated).

    Pipeline: validate → consent check → bot filter → dedupe → aggregate →
    privacy gate (cohort ≥ 30, suppression) → snapshot-ready.
    """
    # TODO: implement aggregation; write snapshots on creator request only.
    return 0
