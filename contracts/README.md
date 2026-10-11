# NEXUS contracts (Foundry)

EVM contracts for the Insight Asset Protocol — ownership and provenance only.
Never store analytics, coordinates, messages, or personal data on-chain.

## Contracts

| Contract | Role |
|----------|------|
| `NexusInsight.sol` | Transfer-restricted ERC-721. One token per insight asset; only `AuctionHouse`/minter can move it |
| `AuctionHouse.sol` | English auctions with escrow, 5% min increment, 10-min anti-sniping, atomic settle + fee |
| `ProvenanceRegistry.sol` | Append-only mint/transfer log (hashes only) |

## Usage

```bash
forge install   # OpenZeppelin + forge-std
forge build
forge test
anvil           # local chain (also via docker compose --profile web3-dev)
```

> On-chain settlement is for cleared jurisdictions only. Nepal production uses
> the fiat rail (`SettlementAdapter`) with a signed off-chain provenance log —
> see the backend `app/services/settlement.py` and design §10.4.
