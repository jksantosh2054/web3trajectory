"""Vault: the current user's owned assets, purchases, validity."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.common import Page

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.get("")
async def get_vault(cursor: str | None = None) -> Page[dict]:
    """Owned insight assets (full analytics access), won auctions, purchase history."""
    _stub()
