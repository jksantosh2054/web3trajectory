"""Creator: posts, feed, publishing."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.common import Page

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.post("/posts", status_code=201)
async def create_post(caption: str | None = None) -> dict:
    """Create a draft post → returns media upload URLs."""
    _stub()


@router.post("/posts/{post_id}/publish", status_code=204)
async def publish_post(post_id: uuid.UUID) -> None:
    """Publish a post (versions it, computes content hash for provenance)."""
    _stub()


@router.get("/feed")
async def get_feed(cursor: str | None = None) -> Page[dict]:
    """Public creator feed."""
    _stub()


@router.get("/posts/{post_id}")
async def get_post(post_id: uuid.UUID) -> dict:
    """Public post page (content only — never analytics)."""
    _stub()
