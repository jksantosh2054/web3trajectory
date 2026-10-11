# API notes

Base path: `/api/v1`. JSON bodies, UUID ids, UTC ISO-8601 timestamps,
cursor pagination, idempotency keys on money-moving calls, RFC-7807 errors.

The canonical contract is the FastAPI OpenAPI schema generated from
`backend/app` — served at `/docs` when the API runs, and validated in CI.

Module overview (see design §9 for full endpoint shapes):

| Prefix | Module |
|--------|--------|
| `/auth`, `/users/me`, `/wallets` | Identity, preferences, consents, wallet linking |
| `/dating` | Presence, pool (distance bands only), proposals, chat, blocks |
| `/seller`, `/market`, `/orders`, `/payments` | Listings, atomic orders, provider webhooks, reviews |
| `/geo` | Geocoding + routing (Valhalla facade) |
| `/posts`, `/feed` | Creator publishing, public feed |
| `/studio` | PRIVATE analytics, snapshot + privacy review |
| `/assets`, `/auctions`, `/vault` | Insight Asset Protocol: mint, teasers, auctions, bids, vault |
| `/admin` | Moderation + compliance (staff only) |
