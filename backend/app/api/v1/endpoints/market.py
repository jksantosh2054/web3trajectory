"""Marketplace: listings, orders, payments, reviews."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.schemas.common import Page
from app.schemas.market import (
    ListingCreate,
    ListingResponse,
    OrderCreate,
    OrderResponse,
    PaymentInitRequest,
    ReviewCreate,
)

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.post("/seller/listings", response_model=ListingResponse, status_code=201)
async def create_listing(body: ListingCreate) -> ListingResponse:
    """Seller creates a draft listing (price NPR, coarse location label)."""
    _stub()


@router.put("/seller/listings/{listing_id}", response_model=ListingResponse)
async def update_listing(listing_id: uuid.UUID, body: ListingCreate) -> ListingResponse:
    _stub()


@router.post("/seller/listings/{listing_id}/publish", status_code=204)
async def publish_listing(listing_id: uuid.UUID) -> None:
    _stub()


@router.post("/seller/listings/{listing_id}/archive", status_code=204)
async def archive_listing(listing_id: uuid.UUID) -> None:
    _stub()


@router.get("/market/listings")
async def search_listings(
    q: str | None = None,
    category: str | None = None,
    bbox: str | None = None,
    cursor: str | None = None,
) -> Page[ListingResponse]:
    """Public spatial/text search over published listings."""
    _stub()


@router.get("/market/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: uuid.UUID) -> ListingResponse:
    _stub()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(body: OrderCreate) -> OrderResponse:
    """Create order + reserve stock atomically (same DB transaction)."""
    _stub()


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID) -> OrderResponse:
    _stub()


@router.post("/payments/{order_id}/initialize", status_code=201)
async def init_payment(order_id: uuid.UUID, body: PaymentInitRequest) -> dict:
    """Start eSewa/Khalti payment. Frontend redirect NEVER marks verified."""
    _stub()


@router.post("/payments/webhooks/{provider}")
async def payment_webhook(provider: str, request: Request) -> dict:
    """Provider-signed webhook — the ONLY path that marks a payment verified."""
    _stub()


@router.post("/orders/{order_id}/fulfill", status_code=204)
async def fulfill_order(order_id: uuid.UUID) -> None:
    """Seller marks the order fulfilled."""
    _stub()


@router.post("/orders/{order_id}/reviews", status_code=201)
async def create_review(order_id: uuid.UUID, body: ReviewCreate) -> dict:
    """Buyer review — only for fulfilled orders, one per order."""
    _stub()
