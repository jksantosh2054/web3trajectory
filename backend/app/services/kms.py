"""KMS interface for insight-asset payload encryption.

Design (see docs §10.5):
- Each asset gets a random 256-bit DEK at mint. Payload encrypted with
  AES-256-GCM → ciphertext to object storage. The DB stores only dek_ref.
- KMS access policy: release the DEK ONLY for the current owner.
- Flow: owner requests /assets/{id}/analytics → backend checks entitlements
  (mirrors token/registry ownership) → KMS decrypt → backend decrypts in
  memory → streams visualization JSON to the owner's session.
- The DEK NEVER reaches the client. On transfer, the policy moves to the new
  owner and the old owner's grants are revoked.

Trust note: this is custodial — the platform could technically access payloads.
Mitigations: KMS audit logging, strict IAM, quarterly access reviews; owner-held
keys (DEK encrypted to owner's wallet pubkey) are the roadmap upgrade.
"""
from __future__ import annotations

import uuid
from typing import Protocol


class KMSAdapter(Protocol):
    async def create_dek(self, asset_id: uuid.UUID) -> str:
        """Generate a per-asset DEK in the KMS. Returns dek_ref (never the key)."""
        ...

    async def decrypt_for_owner(self, dek_ref: str, owner_id: uuid.UUID) -> bytes:
        """Return the raw DEK bytes ONLY if owner_id is the current owner.

        Raises PermissionError otherwise. Callers must hold the plaintext in
        memory only for the duration of the request.
        """
        ...

    async def rotate_policy(self, dek_ref: str, new_owner_id: uuid.UUID) -> None:
        """Move the access policy to the new owner (called on transfer)."""
        ...


class LocalDevKMS:
    """INSECURE dev-only KMS: keys in process memory. Never use in production."""

    def __init__(self) -> None:
        self._keys: dict[str, tuple[bytes, uuid.UUID]] = {}

    async def create_dek(self, asset_id: uuid.UUID) -> str:
        import os

        ref = f"localdek-{uuid.uuid4()}"
        # owner unknown at creation; set via rotate_policy after mint
        self._keys[ref] = (os.urandom(32), asset_id)  # placeholder binding
        return ref

    async def decrypt_for_owner(self, dek_ref: str, owner_id: uuid.UUID) -> bytes:
        key, _bound = self._keys[dek_ref]
        return key

    async def rotate_policy(self, dek_ref: str, new_owner_id: uuid.UUID) -> None:
        key, _bound = self._keys[dek_ref]
        self._keys[dek_ref] = (key, new_owner_id)
