"""Insight Asset Protocol schemas."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SnapshotCreate(BaseModel):
    post_id: uuid.UUID
    window_start: datetime
    window_end: datetime


class PrivacyReport(BaseModel):
    cohort_sizes: dict[str, int]
    suppressed_cells: list[str]
    teaser_preview: dict[str, Any]


class SnapshotResponse(BaseModel):
    snapshot_id: uuid.UUID
    privacy_report: PrivacyReport


class AssetMintRequest(BaseModel):
    snapshot_id: uuid.UUID


class AssetTeaser(BaseModel):
    """Public view — coarse by design."""

    id: uuid.UUID
    post_id: uuid.UUID
    manifest_hash: str
    engagement_band: str  # e.g. "1k–5k views"
    top_districts: list[str]
    status: str
    auction: dict[str, Any] | None = None


class AuctionCreate(BaseModel):
    reserve_price: Decimal = Field(ge=0)
    min_increment_pct: Decimal = Field(default=Decimal("5.00"), ge=0, le=100)
    duration_days: int = Field(ge=1, le=14, default=7)
    buy_now_price: Decimal | None = Field(default=None, ge=0)


class AuctionResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    status: str
    reserve_price: Decimal
    high_bid: Decimal | None = None
    ends_at: datetime
    reserve_met: bool = False


class BidCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    idempotency_key: uuid.UUID


class BidResponse(BaseModel):
    id: uuid.UUID
    amount: Decimal
    status: str
    position: int = 1
