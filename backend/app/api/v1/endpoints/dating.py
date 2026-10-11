"""Dating: presence, pool (bands only), proposals, chat, blocking."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import Page
from app.schemas.dating import (
    BlockRequest,
    MessageCreate,
    MessageResponse,
    PresenceRequest,
    PresenceResponse,
    ProposalRequest,
    ProposalResponse,
)

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.post("/presence", response_model=PresenceResponse, status_code=201)
async def set_presence(body: PresenceRequest) -> PresenceResponse:
    """Go date-ready. Precise coords stored server-side only, short TTL."""
    _stub()


@router.delete("/presence", status_code=204)
async def clear_presence() -> None:
    """Go invisible immediately."""
    _stub()


@router.get("/pool")
async def get_pool(
    radius_m: int = Query(3000, ge=500, le=50000), cursor: str | None = None
) -> Page[dict]:
    """Candidate cards with DISTANCE BANDS only.

    Never returns: coordinates, precise distance, cell ids, live movement,
    group sizes < 5. Rate-limited; order randomized.
    """
    _stub()


@router.post("/proposals", response_model=ProposalResponse, status_code=201)
async def create_proposal(body: ProposalRequest) -> ProposalResponse:
    """Send a date proposal (activity, time, public meeting area)."""
    _stub()


@router.get("/proposals")
async def list_proposals(box: str = Query("received", pattern="^(sent|received)$")) -> Page[dict]:
    _stub()


@router.post("/proposals/{proposal_id}/accept", response_model=ProposalResponse)
async def accept_proposal(proposal_id: uuid.UUID) -> ProposalResponse:
    """Atomic accept: verify identity, validity, 18+, no blocks → create conversation."""
    _stub()


@router.post("/proposals/{proposal_id}/decline", status_code=204)
async def decline_proposal(proposal_id: uuid.UUID) -> None:
    _stub()


@router.post("/proposals/{proposal_id}/withdraw", status_code=204)
async def withdraw_proposal(proposal_id: uuid.UUID) -> None:
    _stub()


@router.get("/conversations/{conversation_id}/messages")
async def list_messages(conversation_id: uuid.UUID, cursor: str | None = None) -> Page[dict]:
    """Cursor-paginated messages for an authorized participant."""
    _stub()


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
async def send_message(conversation_id: uuid.UUID, body: MessageCreate) -> MessageResponse:
    _stub()


@router.post("/blocks", status_code=201)
async def block_user(body: BlockRequest) -> dict:
    """Block: hard mute — no messages, no pool visibility, conversation frozen."""
    _stub()
