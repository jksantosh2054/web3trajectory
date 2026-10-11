# NEXUS

One platform, one identity, one map. A location-aware Web3 super-app launching in Nepal.

## The five experiences

| Experience | What it is |
|------------|-----------|
| **Date** | A live, location-based pool of date-ready people within your chosen radius. Precise locations are never exposed — discovery uses distance bands, jitter, and short-lived presence. You send a **date proposal**; only an accepted proposal unlocks private chat. 18+, opt-in, one-tap block. |
| **Market** | Buy and sell anything — products with or without a store — always with a location, a price in NPR, and reviews from verified buyers. Atomic inventory, eSewa/Khalti payments. |
| **Navigate** | Real-time GPS turn-by-turn navigation on open map data (self-hosted Valhalla + Nepal OSM). GPS traces live in memory only. |
| **Create** | Publish anything — art, video, music, literature. Your content stays yours; copyright never transfers. |
| **Own the insight** | Every post generates a private **engagement-intelligence asset**: *when* and *where* attention flowed to your post, visualized. This insight — not the content — is the tradeable asset. Only its owner can see it in full resolution (encrypted, KMS-gated). Anyone can **bid** in open auctions to buy it. |

**Web3 spine:** EVM-compatible contracts prove *who owns which insight* and *that it hasn't been altered*. The chain never holds locations, messages, or audience data. In Nepal production, crypto settlement is disabled (per the Nepal Rastra Bank notice) — settlement runs on the fiat rail with a signed off-chain provenance log. See `docs/`.

## Quickstart

Prerequisites: Docker + Docker Compose only. No local Python/Node needed.

```bash
cp .env.example .env        # fill in secrets (never commit .env)
docker compose up --build
```

- Web (PWA): http://localhost:3000
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001
- Anvil (chain, `web3-dev` profile only): `docker compose --profile web3-dev up chain`

Run tests:

```bash
docker compose run --rm api pytest
docker compose --profile web3-dev run --rm chain forge test   # from ./contracts
```

## Repo layout

```
apps/web/            # Next.js 14 App Router PWA (TypeScript, MapLibre GL)
backend/             # FastAPI modular monolith
  app/
    api/v1/          # REST routers per module (auth, dating, market, geo, posts, studio, assets, auctions, vault, admin)
    core/            # config (pydantic-settings), security (argon2/JWT), RFC-7807 errors
    db/              # async SQLAlchemy session, declarative base
    models/          # SQLAlchemy 2.0 models mirroring the DDL
    schemas/         # Pydantic v2 request/response schemas
    services/        # SettlementAdapter (fiat/simulated/onchain), KMS interface, privacy helpers
    worker/          # Celery app + tasks (outbox, presence expiry, auction closing, ...)
  alembic/           # migrations (0001_initial_schema.py = full §8 DDL)
contracts/           # Foundry project: NexusInsight (ERC-721), AuctionHouse, ProvenanceRegistry
infrastructure/      # routing/ — Valhalla + Nepal OSM extract (proposed)
docs/                # NEXUS-v2-Complete-Platform-Design.md, ADRs, API notes
```

## Key design pointers

- **Guest-first:** public content needs no account; registration unlocks persistence and roles.
- **Privacy by design:** precise dating coordinates live in one restricted table with short TTL; analytics are aggregation-first (min cohort 30, sparse-cell suppression); full-resolution insight payloads are encrypted and owner-gated.
- **Settlement modes** (`SETTLEMENT_MODE`): `fiat` (Nepal production default), `simulated` (local/CI), `onchain` (future cleared jurisdiction only).
- **Money rule:** a frontend redirect never marks a payment verified — only provider-signed webhooks + reconciliation.

## Docs

- [Complete platform design (v2.0)](docs/NEXUS-v2-Complete-Platform-Design.md) — product, data model, APIs, Web3, privacy, roadmap.
- [Architecture decisions](docs/adr/README.md)
- [API notes](docs/api/README.md)

## Status

Scaffold stage (NX-001…NX-012). Endpoints are real paths/methods with stub bodies; contracts compile under Foundry; the migration creates the full schema. Not production-ready — see the release gates in the design doc §15.
