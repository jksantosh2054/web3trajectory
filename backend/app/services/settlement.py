"""SettlementAdapter — one interface, three rails.

Modes (SETTLEMENT_MODE):
- fiat:      Nepal production. eSewa/Khalti capture at settle; ownership moves in
             Postgres + a SIGNED off-chain provenance log. OnchainSettlement is
             DISABLED here — crypto settlement needs legal clearance (NRB notice).
- simulated: local dev / CI. Mock escrow; full auction flow testable, no money.
- onchain:   future cleared jurisdiction. Bids escrowed in AuctionHouse;
             settle() is atomic on-chain (payment + fee + token transfer).

The product behaves identically from the user's perspective; only the rail changes.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.core.config import settings


@dataclass
class EscrowRef:
    """Reference to funds held for a bid."""

    id: str
    provider: str  # esewa | khalti | manual_sandbox | onchain | simulated
    amount: Decimal
    currency: str = "NPR"


@dataclass
class SettlementReceipt:
    auction_id: uuid.UUID
    winner_id: uuid.UUID
    amount: Decimal
    platform_fee: Decimal
    seller_payout: Decimal
    tx_hash: str | None = None  # on-chain modes
    registry_signature: str | None = None  # fiat mode: platform signature


class SettlementAdapter(Protocol):
    """Contract every settlement rail implements."""

    async def escrow_bid(
        self, auction_id: uuid.UUID, bidder_id: uuid.UUID, amount: Decimal
    ) -> EscrowRef:
        """Hold (or commit) funds for a bid. Called at bid time."""
        ...

    async def release_escrow(self, escrow: EscrowRef) -> None:
        """Release a losing/outbid escrow."""
        ...

    async def settle_auction(
        self,
        auction_id: uuid.UUID,
        asset_id: uuid.UUID,
        winner_id: uuid.UUID,
        amount: Decimal,
        seller_id: uuid.UUID,
    ) -> SettlementReceipt:
        """Atomic settle: capture → fee → payout → ownership transfer.

        Must be all-or-nothing: a failed settlement never grants ownership.
        """
        ...

    async def transfer_asset(
        self, asset_id: uuid.UUID, from_user_id: uuid.UUID | None, to_user_id: uuid.UUID
    ) -> str:
        """Move token/registry ownership. Returns tx_hash or registry_signature."""
        ...


class FiatSettlement:
    """Nepal production rail: eSewa / Khalti.

    Bid-time holds depend on provider pre-auth capability (OPEN QUESTION).
    MVP fallback: bid = binding offer; payment captured within 24h of winning;
    asset transfers on capture; failed payment → next-highest bidder.
    """

    def __init__(self, provider: str = "esewa") -> None:
        assert provider in ("esewa", "khalti", "manual_sandbox"), provider
        self.provider = provider

    async def escrow_bid(
        self, auction_id: uuid.UUID, bidder_id: uuid.UUID, amount: Decimal
    ) -> EscrowRef:
        # TODO: provider pre-auth hold; fallback: record binding offer, no hold.
        raise NotImplementedError

    async def release_escrow(self, escrow: EscrowRef) -> None:
        # TODO: void pre-auth or no-op for binding offers.
        raise NotImplementedError

    async def settle_auction(
        self,
        auction_id: uuid.UUID,
        asset_id: uuid.UUID,
        winner_id: uuid.UUID,
        amount: Decimal,
        seller_id: uuid.UUID,
    ) -> SettlementReceipt:
        # TODO: capture via provider webhook-verified payment; fee = amount * PLATFORM_FEE_PCT;
        # then transfer_asset(); sign provenance record with platform key.
        raise NotImplementedError

    async def transfer_asset(
        self, asset_id: uuid.UUID, from_user_id: uuid.UUID | None, to_user_id: uuid.UUID
    ) -> str:
        # TODO: update insight_assets.owner_id + entitlements in one transaction,
        # update KMS policy, append signed provenance record. Returns registry_signature.
        raise NotImplementedError


class SimulatedSettlement:
    """Local dev / CI rail: no real money, full flow."""

    async def escrow_bid(
        self, auction_id: uuid.UUID, bidder_id: uuid.UUID, amount: Decimal
    ) -> EscrowRef:
        return EscrowRef(id=f"sim-{uuid.uuid4()}", provider="simulated", amount=amount)

    async def release_escrow(self, escrow: EscrowRef) -> None:
        return None

    async def settle_auction(
        self,
        auction_id: uuid.UUID,
        asset_id: uuid.UUID,
        winner_id: uuid.UUID,
        amount: Decimal,
        seller_id: uuid.UUID,
    ) -> SettlementReceipt:
        fee = amount * Decimal(str(settings.platform_fee_pct)) / Decimal(100)
        return SettlementReceipt(
            auction_id=auction_id,
            winner_id=winner_id,
            amount=amount,
            platform_fee=fee,
            seller_payout=amount - fee,
            registry_signature=f"sim-sig-{uuid.uuid4()}",
        )

    async def transfer_asset(
        self, asset_id: uuid.UUID, from_user_id: uuid.UUID | None, to_user_id: uuid.UUID
    ) -> str:
        return f"sim-sig-{uuid.uuid4()}"


class OnchainSettlement:
    """Future cleared-jurisdiction rail: EVM escrow + atomic settle.

    DISABLED in Nepal production by configuration (see config.settlement_mode).
    """

    def __init__(self, rpc_url: str, auction_house: str) -> None:
        self.rpc_url = rpc_url
        self.auction_house = auction_house

    async def escrow_bid(
        self, auction_id: uuid.UUID, bidder_id: uuid.UUID, amount: Decimal
    ) -> EscrowRef:
        # TODO: AuctionHouse.placeBid via relayer / user-signed tx.
        raise NotImplementedError

    async def release_escrow(self, escrow: EscrowRef) -> None:
        # TODO: AuctionHouse refund path.
        raise NotImplementedError

    async def settle_auction(
        self,
        auction_id: uuid.UUID,
        asset_id: uuid.UUID,
        winner_id: uuid.UUID,
        amount: Decimal,
        seller_id: uuid.UUID,
    ) -> SettlementReceipt:
        # TODO: AuctionHouse.settle — atomic: payment + fee + transferRestricted.
        raise NotImplementedError

    async def transfer_asset(
        self, asset_id: uuid.UUID, from_user_id: uuid.UUID | None, to_user_id: uuid.UUID
    ) -> str:
        # TODO: NexusInsight.transferRestricted via AuctionHouse/settle. Returns tx_hash.
        raise NotImplementedError


def get_settlement_adapter() -> SettlementAdapter:
    """Factory driven by SETTLEMENT_MODE. Nepal production must resolve to fiat."""
    mode = settings.settlement_mode.lower()
    if mode == "fiat":
        if settings.is_nepal_production():
            return FiatSettlement(provider="esewa")  # provider chosen per order
        return FiatSettlement()
    if mode == "onchain":
        if settings.is_nepal_production():
            raise RuntimeError("onchain settlement is disabled in Nepal production")
        return OnchainSettlement(
            rpc_url=settings.chain_rpc_url,
            auction_house=settings.auction_house_address,
        )
    return SimulatedSettlement()
