"""Shared Pydantic v2 schemas: envelopes, pagination, geo."""
from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Meta(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class Envelope(BaseModel, Generic[T]):
    data: T
    meta: Meta = Field(default_factory=Meta)


class Page(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None


class LatLng(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class DistanceBandCandidate(BaseModel):
    """What the dating pool is allowed to return — never coordinates."""

    profile_id: uuid.UUID
    display_name: str
    avatar_url: str | None = None
    distance_band: str  # "<1 km" | "1–3 km" | "3–5 km" | "5–10 km" | "10+ km"
    shared_interests: int = 0
    availability: str = "active"


class ErrorDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    request_id: str
    meta: dict[str, Any] | None = None
