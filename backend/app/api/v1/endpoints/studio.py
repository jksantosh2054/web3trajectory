"""Creator Studio: PRIVATE analytics (visibly distinct from public post pages)."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.get("/overview")
async def studio_overview() -> dict:
    """Creator's posts + aggregate private stats."""
    _stub()


@router.get("/posts/{post_id}/analytics")
async def post_analytics(
    post_id: uuid.UUID,
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None, alias="to"),
    granularity: str = Query("day", pattern="^(hour|day|week)$"),
) -> dict:
    """PRIVATE full-resolution analytics: time series, geo distribution, funnel.

    Requires creator ownership. The Studio UI must be visually distinct
    (dark theme + 'PRIVATE' banner) so it is never confused with the public page.
    """
    _stub()


@router.post("/snapshots", status_code=201)
async def create_snapshot(post_id: uuid.UUID, from_: datetime, to: datetime) -> dict:
    """Build an analytics snapshot + privacy report for review BEFORE minting."""
    _stub()
