"""Insight assets: mint, marketplace (teasers), owner-only full analytics."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.assets import AssetMintRequest, AssetTeaser, AuctionCreate, AuctionResponse
from app.schemas.common import Page

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.post("", response_model=AssetTeaser, status_code=201)
async def mint_asset(body: AssetMintRequest) -> AssetTeaser:
    """Mint an insight asset from an approved snapshot.

    Encrypts the full-resolution payload (per-asset DEK via KMS), stores
    ciphertext, computes manifestHash, mints the token (on-chain) or signed
    registry entry (Nepal fiat mode).
    """
    _stub()


@router.get("")
async def list_assets(q: str | None = None, cursor: str | None = None) -> Page[AssetTeaser]:
    """Asset marketplace — teasers only (coarse by design)."""
    _stub()


@router.get("/{asset_id}", response_model=AssetTeaser)
async def get_asset(asset_id: uuid.UUID) -> AssetTeaser:
    """Public asset page: teaser + provenance + auction state."""
    _stub()


@router.get("/{asset_id}/analytics")
async def get_asset_analytics(asset_id: uuid.UUID) -> dict:
    """FULL analytics — requires current-owner entitlement. 403 otherwise.

    Backend verifies entitlement → KMS releases DEK → decrypt in memory →
    stream to owner's session. The DEK never reaches the client.
    """
    _stub()


@router.post("/{asset_id}/auctions", response_model=AuctionResponse, status_code=201)
async def create_auction(asset_id: uuid.UUID, body: AuctionCreate) -> AuctionResponse:
    """Owner starts an English auction (reserve, increment, duration, anti-snipe)."""
    _stub()


@router.get("/{asset_id}/auction", response_model=AuctionResponse)
async def get_auction(asset_id: uuid.UUID) -> AuctionResponse:
    """Live auction state: high bid, time left, reserve met."""
    _stub()
