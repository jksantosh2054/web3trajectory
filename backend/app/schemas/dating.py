"""Dating schemas."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import LatLng


class PresenceRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_m: int = Field(ge=500, le=50000, default=5000)
    availability_minutes: int = Field(ge=5, le=60, default=15)


class PresenceResponse(BaseModel):
    status: str
    expires_at: datetime


class ProposalRequest(BaseModel):
    recipient_id: uuid.UUID
    activity: str = Field(min_length=1, max_length=200)
    proposed_time: datetime | None = None
    meeting_area: str | None = None  # public area name only — never coordinates


class ProposalResponse(BaseModel):
    id: uuid.UUID
    status: str
    conversation_id: uuid.UUID | None = None


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    sent_at: datetime


class BlockRequest(BaseModel):
    user_id: uuid.UUID
