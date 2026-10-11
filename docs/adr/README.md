# Architecture Decision Records

| ID | Decision | Status |
|----|----------|--------|
| ADR-001 | Modular monolith (FastAPI), selectively separated infra | Confirmed |
| ADR-002 | Next.js responsive PWA, no native apps for MVP | Confirmed |
| ADR-003 | PostgreSQL/PostGIS as system of record | Confirmed |
| ADR-004 | MapLibre GL for map UI | Confirmed |
| ADR-005 | Redis Streams for event transport; Celery workers | Confirmed |
| ADR-006 | Private analytics + payloads off-chain, encrypted | Required boundary |
| ADR-007 | Insight assets transfer ownership (sale); copyright never moves | Confirmed product direction |
| ADR-008 | Transfer-restricted ERC-721; settlement only via platform contracts/adapters | Confirmed |
| ADR-009 | EVM-compatible, no proprietary token in MVP | Confirmed |
| ADR-010 | Crypto settlement disabled in Nepal production (NRB notice) | Legal gate |
| ADR-011 | eSewa/Khalti fiat rail; server-verified webhooks only | Confirmed |
| ADR-012 | Kathmandu Valley pilot geography | Proposed |
| ADR-013 | English first, Nepali i18n designed in | Proposed |
| ADR-014 | Valhalla self-hosted routing, Nepal OSM extract | Proposed |
| ADR-015 | Custodial KMS with owner-bound policy (owner-held keys later) | Proposed |
| ADR-016 | 18+ dating, bands+jitter+TTL anti-triangulation | Required safety baseline |
| ADR-017 | Platform fee proposed 5% on auction settlement | Proposed |

Full rationale lives in `docs/NEXUS-v2-Complete-Platform-Design.md` §17.
