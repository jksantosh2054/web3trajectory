"""Auth + identity schemas."""
from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=r"^\+[1-9]\d{7,14}$")
    password: str | None = Field(default=None, min_length=8)
    display_name: str = Field(min_length=1, max_length=80)
    date_of_birth: date | None = None


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = None
    otp: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ConsentRequest(BaseModel):
    purpose: str
    granted: bool
    version: str = "v1"


class WalletLinkRequest(BaseModel):
    chain_id: int
    address: str = Field(pattern=r"^0x[0-9a-fA-F]{40}$")


class WalletVerifyRequest(BaseModel):
    challenge_id: uuid.UUID
    signature: str
