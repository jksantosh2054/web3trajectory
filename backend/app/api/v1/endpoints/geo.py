"""Navigation: geocoding + routing (Valhalla, self-hosted)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import LatLng

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.get("/geocode")
async def geocode(q: str = Query(min_length=1), bias: str | None = None) -> dict:
    """Nepal-first geocoding (Pelias/Nominatim behind this facade)."""
    _stub()


@router.post("/route")
async def route(origin: LatLng, destination: LatLng, profile: str = "car") -> dict:
    """Route geometry + distance + duration + maneuvers. No trace persisted."""
    _stub()
