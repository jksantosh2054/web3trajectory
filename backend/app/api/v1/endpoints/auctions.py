"""Auctions: bidding, cancellation."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.assets import BidCreate, BidResponse

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.post("/{auction_id}/bids", response_model=BidResponse, status_code=201)
async def place_bid(auction_id: uuid.UUID, body: BidCreate) -> BidResponse:
    """Place a bid (idempotent). Must exceed high bid + min increment.

    Escrow per settlement mode: fiat capture-at-settle (or provider hold),
    simulated mock, on-chain escrow in AuctionHouse.
    """
    _stub()


@router.post("/{auction_id}/cancel", status_code=204)
async def cancel_auction(auction_id: uuid.UUID) -> None:
    """Seller cancels — only before the first bid."""
    _stub()
