"""Marketplace schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import LatLng


class ListingCreate(BaseModel):
    product_id: uuid.UUID
    price: Decimal = Field(ge=0)
    location: LatLng
    location_label: str
    stock: int = Field(ge=0, default=1)


class ListingResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    price: Decimal
    currency: str = "NPR"
    location_label: str
    stock: int
    status: str
    published_at: datetime | None = None


class OrderCreate(BaseModel):
    items: list[dict]  # [{listing_id, qty}] — refined in later revisions
    idempotency_key: uuid.UUID


class OrderResponse(BaseModel):
    id: uuid.UUID
    total: Decimal
    currency: str = "NPR"
    status: str


class PaymentInitRequest(BaseModel):
    provider: str = Field(pattern=r"^(esewa|khalti)$")


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    body: str | None = None
