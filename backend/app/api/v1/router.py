"""Aggregate v1 router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    assets,
    auctions,
    auth,
    dating,
    geo,
    market,
    posts,
    studio,
    vault,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dating.router, prefix="/dating", tags=["dating"])
api_router.include_router(market.router, tags=["market"])
api_router.include_router(geo.router, prefix="/geo", tags=["geo"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(studio.router, prefix="/studio", tags=["studio"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(auctions.router, prefix="/auctions", tags=["auctions"])
api_router.include_router(vault.router, prefix="/vault", tags=["vault"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
