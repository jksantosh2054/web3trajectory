"""Admin + compliance: moderation, users, asset approvals, privacy requests."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import Page

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.get("/reports")
async def list_reports(status_: str = Query("open", alias="status")) -> Page[dict]:
    """Moderation queue."""
    _stub()


@router.post("/reports/{report_id}/action", status_code=204)
async def act_on_report(report_id: uuid.UUID, action: str = Query(pattern="^(warn|hide|suspend|dismiss)$")) -> None:
    """Moderator action — writes an audit event."""
    _stub()


@router.get("/compliance/assets")
async def review_assets() -> Page[dict]:
    """Compliance spot-checks of minted assets (provenance + privacy report)."""
    _stub()


@router.get("/compliance/payments")
async def review_payments() -> Page[dict]:
    """Payment disputes and reconciliation exceptions."""
    _stub()
