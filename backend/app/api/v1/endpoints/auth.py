"""Identity: register, login, recovery, consents, wallets."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import (
    ConsentRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    WalletLinkRequest,
    WalletVerifyRequest,
)

router = APIRouter()


def _stub() -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "scaffold stub")


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest) -> TokenResponse:
    """Create an account (email/phone). Guest upgrade path lands here too."""
    _stub()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    """Password or OTP login → session JWT."""
    _stub()


@router.post("/logout", status_code=204)
async def logout() -> None:
    """Invalidate the current session."""
    _stub()


@router.post("/recover", status_code=202)
async def recover(email: str | None = None, phone: str | None = None) -> dict:
    """Start account recovery (email link / phone OTP)."""
    _stub()


@router.delete("/users/me", status_code=204)
async def delete_account() -> None:
    """Delete account per privacy request (subject to legal holds)."""
    _stub()


@router.get("/users/me/preferences/{category}")
async def get_preferences(category: str) -> dict:
    """Read stored preferences for a category (interests, dating, market...)."""
    _stub()


@router.put("/users/me/preferences/{category}")
async def put_preferences(category: str, settings: dict) -> dict:
    """Store preferences — this is what sign-up is for (guest → registered)."""
    _stub()


@router.post("/users/me/consents", status_code=201)
async def set_consent(body: ConsentRequest) -> dict:
    """Grant/revoke a purpose-scoped consent (location, dating, analytics...)."""
    _stub()


@router.get("/users/me/export")
async def export_data() -> dict:
    """Data export for privacy requests."""
    _stub()


@router.post("/wallets/link", status_code=201)
async def link_wallet(body: WalletLinkRequest) -> dict:
    """Begin wallet linking: returns a signature challenge."""
    _stub()


@router.post("/wallets/verify")
async def verify_wallet(body: WalletVerifyRequest) -> dict:
    """Verify the signed challenge and link the wallet."""
    _stub()
