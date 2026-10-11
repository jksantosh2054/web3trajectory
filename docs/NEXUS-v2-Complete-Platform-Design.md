# NEXUS — Complete Platform Design

**Version 2.0 — redesigned from the v1.0 specification**
**Date:** 11 October 2026
**Status:** Implementation-ready design baseline (decisions marked CONFIRMED / PROPOSED / OPEN)

---

## Table of contents

0. Redesign delta — what changed from v1.0 and why
1. Product thesis
2. Confirmed product decisions
3. User roles and permission matrix
4. The Insight Asset Protocol (the Web3 core)
5. User journeys
6. Information architecture — routes and page states
7. Design system and UX requirements
8. Data model (PostgreSQL/PostGIS)
9. API contracts
10. Web3 architecture — contracts, settlement, key management
11. Nepal legal and payments posture
12. Privacy and safety architecture
13. Event-driven architecture and analytics pipeline
14. Infrastructure — Docker, environments, CI/CD
15. Testing strategy and release gates
16. Phased roadmap and sprint backlog
17. Decisions register, open questions, risks
18. What to build first

---

## 0. Redesign delta — what changed from v1.0 and why

The v1.0 spec was a strong skeleton. Reading it against your objective, I made these structural changes:

| # | v1.0 | v2.0 (this design) | Why |
|---|------|--------------------|-----|
| 1 | "Analytics licensing" — creators *license* reports to buyers, copyright stays with creator | **Insight Asset Protocol** — each post's *engagement intelligence* (the time+location flow of its traffic and its visualization) is minted as a **tradeable asset**. Bidding **transfers ownership** of the insight, not just a license. The content's copyright never moves; the *popularity intelligence* does. | Your objective says "bid to purchase the post (post means the insight and visualization)". Licensing becomes a later extension, not the core. |
| 2 | "Only the owner can see the algorithm" stated as a principle | Enforced by construction: full-resolution analytics are **encrypted per asset**; the decryption key is released by a KMS **only to the current on-chain/registry owner**. Teaser views for bidders are coarse by design. | A principle without a mechanism is a wish. Section 10 defines the mechanism. |
| 3 | Dating pool API returned candidates | Added explicit **anti-triangulation** rules: coarse distance bands, jitter, query rate limits, hidden small-group counts, no live movement. | Precise location in dating "can be dangerous" — your words. The v1.0 API shape allowed reconstruction attacks. |
| 4 | SettlementAdapter existed | Wired through **both** marketplace orders and asset auctions; defines exactly what "on-chain" means per environment (local / testnet / Nepal prod / future jurisdiction). | Auctions need settlement too, and Nepal's crypto restriction (NRB notice) applies to auction settlement as much as commerce. |
| 5 | "Routing service" unspecified | **Self-hosted Valhalla + Nepal OSM extract** for routing; Pelias/Nominatim for geocoding; GPS via browser Geolocation; navigation sessions ephemeral. | "Real-time GPS navigation" needs a concrete engine. Valhalla is the pragmatic self-hosted choice. |
| 6 | Guest mode mentioned | **Progressive identity model** fully specified: device session → registered account → independent role grants (dating, seller, creator). | "Without sign-up view; sign-up is just to store preferences" needs exact semantics for what guests can/can't do. |
| 7 | No asset economics | Added: reserve pricing, bid increments, anti-sniping, platform fee (PROPOSED 5%), creator payout, escrow model per settlement mode. | An auction without settlement economics is not implementable. |
| 8 | Moderation as a phase | Safety systems (dating block/report, marketplace verification tiers, asset provenance review) are **release gates**, not later phases. | Dating + commerce cannot pilot without them. |

Everything else from v1.0 that was sound — modular monolith, FastAPI + Next.js PWA, PostgreSQL/PostGIS, transactional outbox, the route inventory, nonfunctional targets — is kept and tightened.

---

## 1. Product thesis

NEXUS is one platform, one identity, one map — five experiences:

1. **Date** — a live, location-based pool of date-ready people within your chosen radius. Precise locations are never exposed. You send a **date proposal**; only an accepted proposal unlocks private chat.
2. **Market** — buy and sell anything: products with or without a store, always with a location, a price in NPR, and reviews from verified buyers.
3. **Navigate** — real-time GPS turn-by-turn navigation built on open map data.
4. **Create** — publish anything (art, video, music, literature). Your content stays yours.
5. **Own the insight** — every post generates a private **engagement-intelligence asset**: *when* and *where* attention flowed to your post, visualized. This insight — not the content — is the tradeable asset. Only its owner can see it in full resolution. Anyone can **bid** to buy it.

The Web3 layer does one job: **verifiable ownership and provenance of insight assets**. It does not hold personal data, locations, messages, or raw analytics. Think of NEXUS as a location-aware Web2 application with a Web3 ownership spine — not a blockchain holding people's lives.

**Launch:** Nepal first (pilot geography PROPOSED: Kathmandu Valley). **Client:** responsive web + PWA. **Scale:** startup MVP.

---

## 2. Confirmed product decisions

| Decision | Status |
|----------|--------|
| Launch market: Nepal | CONFIRMED |
| Client: responsive web + PWA (no native apps for MVP) | CONFIRMED |
| Backend: Python/FastAPI, modular monolith | CONFIRMED |
| Database: PostgreSQL + PostGIS, UUID keys, UTC TIMESTAMPTZ | CONFIRMED |
| Frontend: Next.js (App Router) | CONFIRMED |
| Map rendering: MapLibre GL | CONFIRMED |
| Blockchain: EVM-compatible; **no proprietary token in MVP** | CONFIRMED |
| Asset model: insight-asset **ownership transfer via auction** (licensing later) | CONFIRMED |
| Copyright: never transfers with an insight asset | CONFIRMED |
| Payments: hybrid — eSewa/Khalti fiat in Nepal production; on-chain settlement disabled in Nepal production pending legal clearance (NRB notice) | CONFIRMED |
| Dating: 18+, opt-in, presence expires, no precise coordinates ever exposed | CONFIRMED |
| Guest-first: public content viewable without registration | CONFIRMED |
| Analytics privacy: aggregation-first, min cohort 30 (starting policy), sparse-cell suppression | CONFIRMED |
| Language: English first, Nepali localization designed in from day one | CONFIRMED |
| Currency: NPR; timezone display: Asia/Kathmandu | CONFIRMED |

### Open questions (must resolve before build — see §17)

Pilot geography, payment-provider onboarding (eSewa/Khalti merchant approval + pre-auth capability), public-chain selection, moderation staffing, platform fee, KMS trust model acceptance, legal clearance path for on-chain settlement.

---

## 3. User roles and permission matrix

One account, many roles. Roles are granted independently; no role implies another.

| Role | Capabilities | Requires |
|------|--------------|----------|
| Guest (device session) | Browse public posts, products, places, routes, asset teasers | Nothing |
| Registered user | Profile, preferences, saved items, follows | Email or phone verification |
| Date participant | Presence, pool, proposals, match chat, block/report | 18+ (DOB), dating opt-in consent |
| Seller (individual) | List products without a store, orders, reviews | Phone verification, seller agreement |
| Seller (store) | Storefront page, inventory tools | + business info, verification tier |
| Creator | Publish posts, Studio, private analytics, mint assets, start auctions | Registered user |
| Bidder / buyer | Place bids, buy assets, pay | Registered user + payment method |
| Moderator | Review reports, act on content/sellers/users | Staff grant, MFA |
| Compliance operator | Approve assets, review payments, handle privacy requests | Staff grant, MFA |
| Administrator | Platform config, role grants | Staff grant, MFA |

**Progressive identity rule:** a guest can do everything public. The moment they want persistence (saved items, preferences), dating, selling, creating, or bidding, they register. Registration never asks for more than needed for the role being activated.

---

## 4. The Insight Asset Protocol (the Web3 core)

This is the heart of the redesign. Read it as the contract between product, backend, and chain.

### 4.1 What the asset is — and is not

- A **post** is content (art, video, music, text). Copyright stays with the creator, always.
- An **insight asset** is the *measured popularity* of that post: the timestamped, geolocated flow of attention it received (views, engagement events), aggregated and visualized.
- The asset answers: *when* did attention arrive, *where* did it come from, *how* did it move. That is "the algorithm" the owner alone can see.
- Buying the asset buys **exclusive visibility into that intelligence** — never the content, never the copyright, never the audience's identities.

### 4.2 Asset lifecycle

```
Post published
  → engagement events collected (consented, pseudonymous)
  → analytics engine aggregates (time series + geo distribution + funnel)
  → privacy gate (min cohort, suppression) must PASS
  → creator opens Asset Studio → reviews privacy report → MINT
  → backend: builds full-resolution snapshot
  → encrypts snapshot with per-asset DEK (AES-256-GCM)
  → stores ciphertext in object storage
  → manifestHash = sha256(ciphertext || metadata)
  → mints Insight token (on-chain) or signed registry entry (Nepal fiat mode)
  → asset page created: PUBLIC TEASER only
  → (optional) creator starts auction with reserve
  → bids → settlement → OWNERSHIP TRANSFERS
  → KMS access policy updated → old owner loses access, new owner gains it
```

### 4.3 What each party sees

| Viewer | Sees |
|--------|------|
| Public / bidder (teaser) | Post itself (as published) · total-engagement **band** (e.g. "1k–5k views") · top-3 districts · blurred heatmap image · manifest hash · provenance (post hash, creator, mint time) · auction state |
| Owner (full) | Everything in teaser, plus: full time series (hour/day), district/grid heatmap, traffic-source funnel (impression → view → like → share), top regions table, export (CSV/PNG) |
| Nobody, ever | Individual audience identities, precise event coordinates, raw event rows |

The teaser is the sales pitch; the full resolution is the product. The blur is deliberate: enough to prove the asset is real, too coarse to extract the intelligence.

### 4.4 Ownership semantics

- Ownership = being the current holder of the Insight token (on-chain) or the current registrant (Nepal fiat mode). One owner at a time.
- Transfer happens **only** through platform settlement (auction settle, or owner-initiated transfer via the settlement contract). The token is **transfer-restricted**: arbitrary wallet-to-wallet transfers are blocked so fees, entitlements, and key policies stay in sync.
- On transfer: (1) token moves, (2) off-chain entitlement moves, (3) KMS decryption policy moves, (4) previous owner's sessions/revocable grants are revoked, (5) audit event recorded.
- Previous snapshots stay with the asset (provenance), but only the current owner can decrypt the current full-resolution payload.

### 4.5 Auction mechanics

- **Type:** English auction (ascending bids), on the asset page.
- **Parameters (set by owner):** reserve price (NPR), minimum increment (PROPOSED: 5% or NPR 100, whichever greater), duration (PROPOSED: 1–14 days), anti-sniping extension (PROPOSED: 10 minutes — any bid in the last 10 min extends close by 10 min), optional buy-now price.
- **States:** `draft → scheduled → live → closing → settled | cancelled | expired`
- **Bidding:** idempotency key per bid; each bid must exceed current high + increment; outbid bidders' authorizations are released immediately.
- **Escrow by settlement mode:**
  - `FIAT` (Nepal production): winning bidder's payment is captured at settle via eSewa/Khalti; *bid-time holds* depend on provider pre-auth capability (OPEN QUESTION — if unavailable, MVP uses "commit to buy": bid is a binding offer, payment collected within 24h of winning, asset transfer on capture; failed payment → offer to next-highest bidder).
  - `SIMULATED` (local/test): mock escrow, full flow testable.
  - `ONCHAIN` (future jurisdiction): bids escrowed in the AuctionHouse contract in the settlement token; atomic settle.
- **Settlement (atomic):** verify winner + reserve met → capture payment → deduct platform fee (PROPOSED 5%) → pay creator/owner → transfer token → move entitlement → update KMS policy → notify parties. Any failure → compensating rollback, no partial grants (PAY-001).
- **No sale:** if reserve not met or no bids → asset returns to owner; all authorizations released.

### 4.6 Provenance

Every asset page shows a verifiable chain: post content hash → engagement window → snapshot manifest hash → mint record → transfer history. In `ONCHAIN`/`SIMULATED` modes these are on-chain events; in `FIAT` (Nepal) mode they are **signed off-chain records** (platform key signs each transition; hashes published in a tamper-evident log), so provenance is verifiable without crypto settlement.

---

## 5. User journeys

### J1 — Guest discovers, then registers to save
1. Opens `/` → sees search + public map with posts, products, places. No login wall.
2. Taps a product → detail page, price in NPR, seller info, reviews.
3. Taps "Save" → prompted to register (email/phone, one screen) → preference stored, item saved.
4. Sets interests + home area in `/settings/preferences` → Explore personalizes.

### J2 — Dating: pool → proposal → chat
1. Registered user, 18+, opens `/dating` → sees opt-in explainer → enables "date-ready", sets radius (default 5 km) and availability (15/30/60 min).
2. Pool shows candidate cards: photo, display name, **distance band** ("1–3 km"), shared interests. Never a map pin, never a precise distance.
3. Sends **proposal**: activity ("Coffee"), proposed time, optional public meeting area.
4. Recipient gets notification → views proposal (sender's card + proposal detail) → Accept / Decline / Let expire (48h).
5. On accept: conversation opens in `/messages/[id]`; both can chat. Either can **block** at any time → conversation frozen, both removed from each other's pool, no location ever disclosed.
6. Presence auto-expires; user can go invisible anytime.

### J3 — Marketplace: list → order → review
1. Seller (individual, no store) lists a product: title, photos, price NPR, pickup location (coarse), stock count.
2. Buyer finds it on map/list → product page → "Buy" → checkout → pays via eSewa/Khalti.
3. **Atomicity:** stock reserved in the same DB transaction as order creation; payment webhook (server-verified, never frontend redirect) confirms → order `paid`.
4. Seller marks fulfilled → buyer can leave a review (only verified fulfilled orders can review).
5. Two buyers racing for the last unit: one wins, the other gets a clean "just sold" state — never oversold.

### J4 — Navigation
1. User opens `/navigate` → searches destination (geocoded, Nepal-first results) → route drawn with distance, duration, maneuvers.
2. Taps "Start" → browser GPS tracks position → turn-by-turn prompts → auto-reroute on deviation.
3. GPS trace lives **in memory only**; nothing persisted unless the user explicitly saves the place/route.

### J5 — Creator: post → insight → asset → auction
1. Creator publishes a post (photo set, video, audio, or text) from `/create`.
2. Engagement accumulates. In `/studio`, the creator sees **private** analytics (visibly distinct UI from the public post page — different header, "Private" badge).
3. Creator opens `/studio/assets/new`, picks the post + time window → platform runs the **privacy review**: shows what will be suppressed, cohort sizes, what the teaser will reveal. Creator approves → **mint**.
4. Asset page `/assets/[id]` goes live with teaser. Creator starts auction: reserve NPR 5,000, 7 days.
5. Bidder places bids; outbid notifications via WebSocket. Auction closes → winner pays → ownership transfers → winner (now owner) sees full analytics in `/vault`.
6. Original creator keeps the post and copyright; the *insight* now belongs to the buyer.

### J6 — Moderation & compliance
1. User reports a profile, listing, post, or message → report lands in `/admin` queue with context.
2. Moderator acts: warn / hide / suspend; every action writes an audit event.
3. Compliance operator reviews newly minted assets (spot-check provenance + privacy report) and payment disputes in `/admin/compliance`.

---

## 6. Information architecture

### 6.1 Route inventory

| Page | Route | Core UI |
|------|-------|---------|
| Landing | `/` | Search, public discovery, featured categories |
| Explore | `/explore` | Map + filters + nearby public results (posts, products, places) |
| Login / Register | `/auth/login`, `/auth/register` | Credentials, recovery, consent |
| Preferences | `/settings/preferences` | Interests, radius, language |
| Privacy | `/settings/privacy` | Consents, location controls, data export, deletion |
| Wallet | `/settings/wallet` | Wallet linking, verification, network (Web3) |
| Dating pool | `/dating` | Safe candidate cards + filters |
| Dating profile | `/dating/profile` | Visibility, availability, preferences |
| Proposals | `/dating/proposals` | Sent / received / accepted / expired |
| Chat | `/messages/[conversationId]` | Authorized private conversation |
| Marketplace | `/market` | Search, product list + map |
| Product | `/market/products/[id]` | Price, seller, stock, reviews |
| Seller storefront | `/shops/[slug]` | Products, reviews, pickup options |
| Seller dashboard | `/seller` | Listings, inventory, orders |
| Checkout | `/checkout` | Order review + payment |
| Orders | `/orders` | Status, history, reviews |
| Navigation | `/navigate` | GPS, destination, route guidance |
| Creator feed | `/feed` | Public content + engagement |
| New post | `/create` | Media, caption, publication settings |
| Post detail | `/posts/[id]` | Content, engagement, provenance |
| Creator Studio | `/studio` | Posts + private analytics overview |
| Post analytics (private) | `/studio/posts/[id]/analytics` | Timeline, heatmap, funnel — "Private" badged |
| Asset builder | `/studio/assets/new` | Scope, privacy review, mint |
| Asset marketplace | `/assets` | Searchable assets (teasers) |
| Asset detail | `/assets/[id]` | Teaser, provenance, auction entry |
| Auction | `/assets/[id]/auction` | Bids, reserve, countdown, settlement |
| My vault | `/vault` | Owned assets (full analytics), purchases, validity |
| Administration | `/admin` | Moderation, users, incidents |
| Compliance | `/admin/compliance` | Asset approvals, payments, privacy requests |

### 6.2 Page-state requirements

Every page implements: **loading · empty · success · validation-error · permission-denied · network-failure**. No exceptions — this is a release gate item.

### 6.3 Key UX rules

- **Mobile-first**, responsive PWA (installable, offline shell, graceful permission prompts for location).
- **Private vs public must look different:** the creator's private analytics screen uses a distinct dark "Studio" theme with a persistent "PRIVATE — only you can see this" banner. No confusion about what is shared.
- **Location permission:** explicit, contextual prompts ("NEXUS needs your location to show nearby dates"); coarse-mode fallback when denied.
- **Low bandwidth:** image variants (thumbnail/standard), lazy media, skeletons.
- **Accessibility:** WCAG 2.2 AA target — keyboard navigation, screen-reader labels, contrast.
- **Localization:** English first; all strings externalized for Nepali; Unicode search; NPR formatting (`रू 1,250`); Nepal Time (Asia/Kathmandu) display; Nepal address formats.

---

## 7. Design system

| Token | Value |
|-------|-------|
| Primary | `#4F46E5` (indigo-600) — actions, links |
| Accent | `#7C3AED` (violet) — Web3/asset surfaces |
| Success / Warning / Danger | `#16A34A` / `#D97706` / `#DC2626` |
| Surface / Ink | `#FFFFFF` / `#0F172A` (slate-900); Studio dark: `#0B1220` bg |
| Font (Latin) | Inter, system fallback |
| Font (Nepali) | Noto Sans Devanagari |
| Radius | 12px cards, 8px inputs, full pills for chips |
| Map style | MapLibre light streets; dark variant for Studio |

Map-first layout pattern: persistent bottom nav (Explore · Social · Market · Create · Me), context panels sliding over the map. Dating, marketplace, and asset discovery all reuse the same map shell with module-specific layers and filters.

---

## 8. Data model (PostgreSQL 17 + PostGIS)

Conventions: UUID primary keys (`gen_random_uuid()`), `TIMESTAMPTZ` in UTC everywhere, `created_at`/`updated_at` on mutable rows, `NUMERIC(18,2)` for NPR, foreign keys + check constraints enforced in the DB (not just the app).

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============ IDENTITY ============
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email CITEXT UNIQUE,
    phone TEXT UNIQUE,                       -- E.164, nullable
    password_hash TEXT,                      -- Argon2id; null for phone-OTP-only
    date_of_birth DATE,                      -- required for dating role
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active','suspended','deleted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

CREATE TABLE profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    bio TEXT,
    avatar_key TEXT,                         -- object-storage key
    visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (visibility IN ('public','private'))
);

CREATE TABLE user_preferences (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,                  -- interests, dating, market, ...
    settings_json JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (user_id, category)
);

CREATE TABLE user_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,                   -- precise_location, dating_presence,
                                             -- engagement_measurement, analytics_licensing, marketing
    version TEXT NOT NULL,
    granted_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_consents_user_purpose ON user_consents (user_id, purpose);

CREATE TABLE wallet_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chain_id BIGINT NOT NULL,
    address TEXT NOT NULL,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (chain_id, address)
);

CREATE TABLE blocks (                        -- user blocks user: both directions muted
    blocker_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (blocker_id, blocked_id),
    CHECK (blocker_id <> blocked_id)
);

-- ============ DATING ============
CREATE TABLE date_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    tagline TEXT,
    interests TEXT[] NOT NULL DEFAULT '{}',
    visibility TEXT NOT NULL DEFAULT 'pool'
        CHECK (visibility IN ('pool','hidden')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Precise location lives here ONLY. Restricted role; short TTL; never joined to public queries.
CREATE TABLE date_presence (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    precise_location GEOGRAPHY(Point, 4326) NOT NULL,
    radius_m INTEGER NOT NULL CHECK (radius_m BETWEEN 500 AND 50000),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_presence_geo ON date_presence USING GIST (precise_location);
CREATE INDEX idx_presence_expiry ON date_presence (expires_at);

CREATE TABLE date_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity TEXT NOT NULL,
    proposed_time TIMESTAMPTZ,
    meeting_area TEXT,                        -- public area name, never coordinates
    status TEXT NOT NULL DEFAULT 'sent'
        CHECK (status IN ('sent','accepted','declined','expired','withdrawn')),
    proposed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT now() + INTERVAL '48 hours',
    CHECK (sender_id <> recipient_id)
);
CREATE INDEX idx_proposals_recipient ON date_proposals (recipient_id, status);
CREATE INDEX idx_proposals_sender ON date_proposals (sender_id, status);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL UNIQUE REFERENCES date_proposals(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open','closed','blocked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body_ciphertext TEXT NOT NULL,            -- encrypted at rest (app-level)
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_conv_time ON messages (conversation_id, sent_at);

-- ============ MARKETPLACE ============
CREATE TABLE sellers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id),
    type TEXT NOT NULL CHECK (type IN ('individual','store')),
    display_name TEXT NOT NULL,
    slug TEXT UNIQUE,                         -- stores only
    verification_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK (verification_status IN ('unverified','phone','id','business')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES sellers(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price NUMERIC(18,2) NOT NULL CHECK (price >= 0),
    currency TEXT NOT NULL DEFAULT 'NPR' CHECK (currency = 'NPR'),  -- MVP: NPR only
    location GEOGRAPHY(Point, 4326) NOT NULL, -- pickup / store point (coarse is fine)
    location_label TEXT NOT NULL,             -- human-readable area shown publicly
    stock INTEGER NOT NULL DEFAULT 1 CHECK (stock >= 0),
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','published','archived','sold_out')),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_listings_geo ON listings USING GIST (location);
CREATE INDEX idx_listings_status ON listings (status);

CREATE TABLE inventory_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES listings(id),
    order_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    expires_at TIMESTAMPTZ NOT NULL,          -- released if unpaid
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id UUID NOT NULL REFERENCES users(id),
    seller_id UUID NOT NULL REFERENCES sellers(id),
    total NUMERIC(18,2) NOT NULL CHECK (total >= 0),
    currency TEXT NOT NULL DEFAULT 'NPR',
    status TEXT NOT NULL DEFAULT 'created'
        CHECK (status IN ('created','payment_pending','paid','fulfilled',
                          'completed','cancelled','refunded')),
    idempotency_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_orders_buyer ON orders (buyer_id, created_at DESC);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES listings(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(18,2) NOT NULL
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    auction_id UUID,                          -- or auction settlement
    provider TEXT NOT NULL CHECK (provider IN ('esewa','khalti','manual_sandbox','onchain')),
    provider_reference TEXT,
    amount NUMERIC(18,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'NPR',
    status TEXT NOT NULL DEFAULT 'initiated'
        CHECK (status IN ('initiated','pending','verified','settled','failed','refunded')),
    idempotency_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, provider_reference)
);

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL UNIQUE REFERENCES orders(id),  -- one review per fulfilled order
    reviewer_id UUID NOT NULL REFERENCES users(id),
    listing_id UUID NOT NULL REFERENCES listings(id),
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ CREATOR / POSTS ============
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    visibility TEXT NOT NULL DEFAULT 'public' CHECK (visibility IN ('public','private')),
    published_at TIMESTAMPTZ,
    current_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_posts_creator ON posts (creator_id, published_at DESC);

CREATE TABLE post_versions (
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    media_keys TEXT[] NOT NULL DEFAULT '{}',
    caption TEXT,
    content_hash TEXT NOT NULL,               -- sha256 of canonical bytes; provenance anchor
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (post_id, version)
);

-- High-volume; partition by month in production.
CREATE TABLE engagement_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    actor_ref TEXT NOT NULL,                  -- pseudonymous viewer id (NOT user_id)
    event_type TEXT NOT NULL
        CHECK (event_type IN ('impression','view','like','share','comment','click')),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    geo_bucket TEXT NOT NULL,                 -- district code or approved grid cell; never precise
    consent_ref TEXT NOT NULL,                -- consent version at event time
    view_duration_ms INTEGER
);
CREATE INDEX idx_eng_post_time ON engagement_events (post_id, occurred_at DESC);

-- ============ INSIGHT ASSETS ============
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    manifest_hash TEXT NOT NULL,              -- sha256(ciphertext || metadata)
    object_key TEXT NOT NULL,                 -- encrypted payload in object storage
    dek_ref TEXT NOT NULL,                    -- KMS reference to per-asset DEK (never the key)
    privacy_report JSONB NOT NULL,            -- cohort sizes, suppressed cells, teaser params
    status TEXT NOT NULL DEFAULT 'ready' CHECK (status IN ('ready','superseded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (window_end > window_start)
);

CREATE TABLE insight_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),   -- = on-chain tokenId (uint256 of uuid)
    snapshot_id UUID NOT NULL REFERENCES analytics_snapshots(id),
    post_id UUID NOT NULL REFERENCES posts(id),
    creator_id UUID NOT NULL REFERENCES users(id),
    owner_id UUID NOT NULL REFERENCES users(id),     -- current owner (registry mirror)
    chain_id BIGINT,                                 -- null in Nepal FIAT mode
    token_address TEXT,                              -- null in Nepal FIAT mode
    manifest_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'minted'
        CHECK (status IN ('minted','auction_live','sold','transferred','retired')),
    minted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_assets_owner ON insight_assets (owner_id, status);
CREATE INDEX idx_assets_post ON insight_assets (post_id);

CREATE TABLE auctions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES insight_assets(id),
    seller_id UUID NOT NULL REFERENCES users(id),
    reserve_price NUMERIC(18,2) NOT NULL CHECK (reserve_price >= 0),
    min_increment_pct NUMERIC(5,2) NOT NULL DEFAULT 5.00,
    buy_now_price NUMERIC(18,2),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    anti_snipe_minutes INTEGER NOT NULL DEFAULT 10,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','scheduled','live','closing','settled','cancelled','expired')),
    winner_id UUID REFERENCES users(id),
    winning_bid_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (ends_at > starts_at)
);
CREATE INDEX idx_auctions_status_end ON auctions (status, ends_at);

CREATE TABLE bids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auction_id UUID NOT NULL REFERENCES auctions(id) ON DELETE CASCADE,
    bidder_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(18,2) NOT NULL CHECK (amount > 0),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active','outbid','winning','won','lost','refunded')),
    idempotency_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_bids_auction_amount ON bids (auction_id, amount DESC);

CREATE TABLE ownership_transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES insight_assets(id),
    from_user_id UUID REFERENCES users(id),
    to_user_id UUID NOT NULL REFERENCES users(id),
    auction_id UUID REFERENCES auctions(id),
    tx_hash TEXT,                             -- on-chain modes
    registry_signature TEXT,                  -- FIAT mode: platform signature over transition
    transferred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE entitlements (                   -- who may currently decrypt/view what
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES insight_assets(id) ON DELETE CASCADE,
    principal_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scope_json JSONB NOT NULL DEFAULT '{"view":"full"}',
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ,
    UNIQUE (asset_id, principal_id)
);

-- ============ OPS ============
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID REFERENCES users(id),
    action TEXT NOT NULL,                     -- e.g. asset.minted, auction.settled, user.suspended
    resource_type TEXT NOT NULL,
    resource_id UUID,
    meta JSONB NOT NULL DEFAULT '{}',
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_actor_time ON audit_events (actor_id, occurred_at DESC);
CREATE INDEX idx_audit_resource ON audit_events (resource_type, resource_id);

CREATE TABLE outbox_events (                  -- transactional outbox
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);
CREATE INDEX idx_outbox_unpublished ON outbox_events (created_at) WHERE published_at IS NULL;

CREATE TABLE reports (                        -- moderation reports
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id),
    target_type TEXT NOT NULL CHECK (target_type IN ('user','post','listing','message','asset')),
    target_id UUID NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','reviewing','actioned','dismissed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 9. API contracts

Base: `/api/v1` · JSON · UUID ids · UTC ISO-8601 · cursor pagination · idempotency keys on payments/orders/bids · RFC-7807 errors · OpenAPI generated from FastAPI, validated in CI.

**Envelopes**
```json
// success
{"data": {"id": "uuid", "status": "active"}, "meta": {"request_id": "uuid"}}
// error
{"type": "https://nexus.example/errors/forbidden", "title": "Forbidden",
 "status": 403, "detail": "Insufficient permission", "request_id": "uuid"}
```

### 9.1 Identity & preferences
```
POST /api/v1/auth/register        {email|phone, password|otp} → session
POST /api/v1/auth/login           {email|phone, password|otp} → session
POST /api/v1/auth/logout
POST /api/v1/auth/recover         {email|phone} → recovery flow
DELETE /api/v1/users/me
GET|PUT /api/v1/users/me/preferences/{category}
POST /api/v1/users/me/consents    {purpose, granted: bool, version}
GET /api/v1/users/me/export       → GDPR-style data export (Privacy Act aligned)
POST /api/v1/wallets/link         {chain_id, address} → challenge
POST /api/v1/wallets/verify       {challenge_id, signature}
```

### 9.2 Dating
```
POST /api/v1/dating/presence
  {latitude, longitude, radius_m, availability_minutes}
  → {status: active, expires_at}                      # precise coords stored server-side only
DELETE /api/v1/dating/presence                        # go invisible

GET /api/v1/dating/pool?radius_m=3000&cursor=
  → {candidates: [{profile_id, display_name, avatar_url,
       distance_band: "<1 km"|"1–3 km"|"3–5 km"|"5–10 km"|"10+ km",
       shared_interests: n, availability: active}],
       next_cursor}
  # NEVER: coordinates, precise distance, cell ids, live movement, group sizes < 5

POST /api/v1/dating/proposals
  {recipient_id, activity, proposed_time, meeting_area?}
POST /api/v1/dating/proposals/{id}/accept   → {proposal_status: accepted, conversation_id}
POST /api/v1/dating/proposals/{id}/decline
POST /api/v1/dating/proposals/{id}/withdraw
POST /api/v1/users/{id}/block               → freezes conversations + pool exclusion
```
Accept is atomic: verifies recipient identity, proposal validity/expiry, both 18+, no block either direction — then creates the conversation in the same transaction.

### 9.3 Marketplace
```
POST /api/v1/seller/listings                # create draft
PUT  /api/v1/seller/listings/{id}           # edit
POST /api/v1/seller/listings/{id}/publish
POST /api/v1/seller/listings/{id}/archive
GET  /api/v1/market/listings?bbox=&q=&category=&cursor=
GET  /api/v1/market/listings/{id}
POST /api/v1/orders                          {items:[{listing_id, qty}], idempotency_key}
GET  /api/v1/orders/{id}
POST /api/v1/payments/{order_id}/initialize  {provider: esewa|khalti}
POST /api/v1/payments/webhooks/{provider}    # provider-signed; ONLY path that marks verified
POST /api/v1/orders/{id}/fulfill             # seller
POST /api/v1/orders/{id}/reviews            # buyer, only when fulfilled
```
Order creation reserves stock (`inventory_reservations`) in the same transaction. Reservation TTL PROPOSED 30 min; expiry releases stock via worker.

### 9.4 Navigation
```
GET /api/v1/geo/geocode?q=&bias=            # Nepal-first geocoding
POST /api/v1/geo/route                       # {origin, destination, profile: foot|bike|car}
  → {distance_m, duration_s, geometry, maneuvers[]}
WS  /ws/navigation/{sessionId}               # position updates → reroute events (ephemeral)
```
Routing engine: self-hosted Valhalla with Nepal OSM extract (PROPOSED). No GPS trace persisted server-side.

### 9.5 Creator & posts
```
POST /api/v1/posts                          # → upload URLs for media
POST /api/v1/posts/{id}/publish
GET  /api/v1/feed?cursor=                   # public feed
GET  /api/v1/posts/{id}                     # public post page
GET  /api/v1/studio/overview
GET  /api/v1/studio/posts/{post_id}/analytics?from=&to=&granularity=hour|day|week
  # PRIVATE — requires creator; returns full-resolution series + geo + funnel
```

### 9.6 Insight assets & auctions (the novel core)
```
POST /api/v1/studio/snapshots
  {post_id, from, to} → {snapshot_id, privacy_report}
  # privacy_report: {cohort_sizes, suppressed_cells, teaser_preview} — creator reviews BEFORE mint

POST /api/v1/assets
  {snapshot_id} → {asset_id, manifest_hash, teaser_url}
  # MINT: encrypts payload, stores ciphertext, mints token / registry entry

GET  /api/v1/assets?cursor=&q=              # asset marketplace — teasers only
GET  /api/v1/assets/{id}                    # teaser + provenance + auction state (public)
GET  /api/v1/assets/{id}/analytics          # FULL — requires current-owner entitlement; 403 otherwise

POST /api/v1/assets/{id}/auctions
  {reserve_price, min_increment_pct?, duration_days, buy_now_price?} → {auction_id}
GET  /api/v1/assets/{id}/auction            # live state: high bid, time left, reserve met?
POST /api/v1/auctions/{id}/bids             {amount, idempotency_key} → {bid_id, position}
POST /api/v1/auctions/{id}/cancel           # seller, only before first bid
GET  /api/v1/vault                          # my owned assets + won auctions + purchase history
```
The licensed-analytics endpoint evaluates, in order: active entitlement → requested metric → date range → geographic granularity → query budget → then returns. Expiry enforced server-side.

### 9.7 WebSocket channels
| Channel | Events |
|---------|--------|
| `/ws/conversations/{id}` | message.created / delivered / read |
| `/ws/notifications` | proposal.received, order.paid, bid.outbid, auction.closing, moderation.* |
| `/ws/auctions/{id}` | bid.placed, auction.extended, auction.settled |
| `/ws/navigation/{sessionId}` | reroute, arrival (ephemeral) |

Authenticated subscribe, per-event authorization, heartbeats, bounded queues, reconnect with cursor.

---

## 10. Web3 architecture

### 10.1 What the chain holds — and never holds

**On-chain:** asset commitments (`assetId → manifestHash`), token ownership, auction escrow/settlement (on-chain mode), license/transfer events.
**Never on-chain:** raw engagement data, precise coordinates, messages, audience identities, personal data of any kind.

### 10.2 Contracts (Solidity ^0.8.24, OpenZeppelin)

| Contract | Responsibility |
|----------|----------------|
| `NexusInsight` (ERC-721) | One token per insight asset; `tokenId = uint256(asset UUID)`; transfer-restricted: only `AuctionHouse` (settle) or `MINTER_ROLE` (platform) can move tokens |
| `AuctionHouse` | Create auction, escrow bids (on-chain mode), anti-snipe extension, atomic settle, fee split, refunds |
| `ProvenanceRegistry` | Append-only mint/transfer event log with manifest hashes (cheap verifiability even when settlement is fiat) |
| `LicenseRegistry` | *Later:* time-bound access grants without ownership transfer |

```solidity
pragma solidity ^0.8.24;

interface INexusInsight {
    event AssetMinted(bytes32 indexed assetId, bytes32 manifestHash, address indexed creator);
    event AssetTransferred(bytes32 indexed assetId, address indexed from, address indexed to, bytes32 settlementRef);

    function mint(bytes32 assetId, address to, bytes32 manifestHash, string calldata metadataURI) external;
    function manifestOf(bytes32 assetId) external view returns (bytes32);
    function transferRestricted(bytes32 assetId, address to, bytes32 settlementRef) external;
}

interface IAuctionHouse {
    event AuctionSettled(bytes32 indexed auctionId, bytes32 indexed assetId, address winner, uint256 amount);

    function createAuction(bytes32 auctionId, bytes32 assetId, uint64 endsAt, uint256 reserve) external;
    function placeBid(bytes32 auctionId) external payable;
    function settle(bytes32 auctionId) external;
    function cancel(bytes32 auctionId) external;
}
```
Full implementation needs: roles, nonces, replay protection, revocation, exclusivity checks, pausability, UUPS upgradeability (PROPOSED, timelocked). Foundry: unit + fuzz + invariant tests; local Anvil; public chain only after legal clearance + independent audit.

### 10.3 Contract invariants
- An assetId can never be minted twice or with a conflicting manifestHash.
- A license/transfer can never be issued for an unminted asset.
- `settle` is atomic: payment capture + fee + token transfer + event — all or nothing.
- Expired/cancelled auctions cannot settle; bids on them are refundable.
- No double-spend of escrowed balances; failed settlement never grants access.

### 10.4 SettlementAdapter — the Nepal answer

```python
class SettlementAdapter(Protocol):
    def escrow_bid(...) -> EscrowRef: ...
    def release_escrow(...) -> None: ...
    def settle_auction(...) -> SettlementReceipt: ...
    def transfer_asset(...) -> TransferReceipt: ...

class FiatSettlement(SettlementAdapter):      # Nepal production
class SimulatedSettlement(SettlementAdapter):# local dev / CI
class OnchainSettlement(SettlementAdapter):  # future cleared jurisdiction
```

| Environment | Settlement | Chain usage |
|-------------|-----------|-------------|
| Local dev | `SIMULATED` | Full contracts on Anvil, mock tokens |
| CI / staging | `SIMULATED` | Anvil or testnet, simulated assets |
| **Nepal production** | **`FIAT`** | **No crypto settlement.** Provenance via `ProvenanceRegistry`-equivalent **signed off-chain log** (platform key signs each mint/transfer; hashes tamper-evident). Ownership registry in Postgres; wallet linking optional. |
| Future cleared jurisdiction | `ONCHAIN` | Real EVM settlement |

The product works identically in all modes from the user's perspective; only the settlement rail changes. This is what makes the Web3 concept shippable under Nepal's current crypto restriction.

### 10.5 Key management — "only the owner sees the algorithm"

- Each asset gets a random 256-bit **Data Encryption Key (DEK)** at mint. Payload encrypted with AES-256-GCM → ciphertext to object storage.
- The DEK itself lives in a **KMS** (managed HSM or self-hosted Vault — PROPOSED: managed KMS in production). The database stores only a `dek_ref`, never the key.
- KMS access policy: **release the DEK only for the current owner**. Backend flow: owner requests `/assets/{id}/analytics` → backend checks `entitlements` (mirrors token ownership; reconciled with chain/registry) → KMS decrypt → backend decrypts payload in memory → streams the visualization JSON to the owner's session. **The DEK never reaches the client.**
- On transfer: entitlement moved, KMS policy updated to new owner, old owner's grants revoked. Previous owner cannot decrypt again.
- Trust note (honest): this is custodial key management — the platform *could* technically access payloads. Mitigations: KMS audit logging, strict IAM, quarterly access reviews; roadmap option for owner-held keys (encrypt DEK to owner's wallet public key) once UX allows. This is documented, not hidden.

### 10.6 Payments (fiat rail)
```
PaymentProvider
 ├── EsewaAdapter
 ├── KhaltiAdapter
 ├── ManualSandboxAdapter
 └── OnchainAdapter        # DISABLED in Nepal production
```
State machine: `initiated → pending → verified → settled`, plus `failed / refunded`. **A frontend redirect is never sufficient to mark verified** — only the provider-signed webhook + independent status reconciliation. Idempotency keys on every money-moving call.

---

## 11. Nepal legal and payments posture

**Critical constraint:** Nepal Rastra Bank's website continues to display a notice identifying virtual-currency/cryptocurrency transactions as illegal. Therefore:

1. **No real-money crypto auctions, token trading, or crypto settlement in Nepal production** without authoritative legal clearance. The `OnchainSettlement` adapter is disabled by configuration in Nepal prod.
2. Cryptographic **signatures, content hashes, and the signed provenance log** are not currency transactions — they ship in Nepal prod and give the Web3 verifiability story without touching the restriction.
3. Commerce and auction payments in Nepal go through **eSewa / Khalti** (merchant onboarding required) with server-side verification.

**Legal review gates (external Nepalese counsel, before public launch):**
- Privacy Act, 2075 and Electronic Transactions Act, 2063 — privacy policy, consent model, data retention, breach handling.
- Marketplace operation: merchant registration, consumer protection, taxation (VAT/PAN implications for sellers and platform fees).
- Dating service: age verification expectations, safety obligations.
- Analytics/insight assets: is selling aggregated engagement intelligence a regulated activity? What disclosures do buyers/sellers need?
- Cross-border data processing (hosting, backups, KMS location).

These reviews are **release gates**, not background tasks.

---

## 12. Privacy and safety architecture

### 12.1 Dating privacy (non-negotiable)
- 18+ eligibility; date-ready **off by default**; presence TTL 15 min default (max 60).
- Discovery returns **distance bands only**, with small random jitter; pool queries rate-limited (PROPOSED: 1 per 30s per user); result order randomized.
- Never exposed: precise coordinates, precise distance, live movement, cell/grid ids that permit reconstruction, group sizes under 5 (shown as "5+").
- `date_presence` is a restricted table: separate DB role, no access from analytics workers, short retention (rows deleted at expiry + grace).
- One-tap **block** and **report** on every dating surface; block = hard mute (no messages, no pool visibility, existing conversation frozen).

### 12.2 Analytics privacy
| Control | Policy |
|---------|--------|
| Minimum distinct actors per released bucket | 30 (starting policy — not proof of anonymity) |
| Geographic resolution in buyer/owner views | District or approved coarse grid; precise event coords prohibited everywhere |
| Sparse-cell suppression | Required; suppressed cells reported in the privacy report |
| Individual audience identifiers in any report | Prohibited |
| Repeated overlapping queries | Budgeted and monitored (query budget per asset per principal) |
| Raw engagement events | 30-day retention, then aggregate-or-delete |
| Snapshot payload | Encrypted; owner-only decryption via KMS policy |

Known limitation (stated openly): combining multiple geo/temporal queries can still leak individuals. The privacy report shown at mint time lists exactly what was suppressed; stronger aggregation or differential privacy may be required as datasets grow.

### 12.3 Consent separation
Independent toggles for: precise location (navigation) · approximate location (discovery) · dating presence · content geotagging · engagement measurement · commercial insight assets · marketing. Withdrawal affects future collection/use. Previously sold assets: copies lawfully transferred cannot be clawed back — the terms of sale state this plainly.

### 12.4 Threat model (abridged)
| Threat | Primary defense |
|--------|-----------------|
| Location stalking (dating) | Bands + jitter + rate limits + TTL + no coordinates in API |
| Harassment | Block/report, proposal limits, moderation queue |
| Fake profiles/sellers | Verification tiers, risk signals, verified-purchase reviews |
| Payment fraud | Provider-signed webhooks, idempotency, reconciliation jobs |
| Insight theft | Owner-only KMS decryption, entitlements, query budgets |
| Re-identification | Cohort minimums, suppression, query budgets |
| Contract exploit | Audit, invariant tests, restricted roles, pausability |
| Insider misuse | Least privilege, DB role separation, audit trails, access reviews |

### 12.5 Security checklist (release gate — 0/12 at kickoff)
HttpOnly secure cookies + CSRF · Argon2id hashing · MFA for staff/financial actions · object-level authorization on every endpoint · signed short-lived media URLs · secrets out of source/images · DB roles by sensitivity · privileged-access audit logs · dependency/container scanning · backup restore drills · contract fuzz/invariant tests · pre-launch pentest.

---

## 13. Event-driven architecture and analytics pipeline

**Transactional outbox from day one:** business write + `outbox_events` row in one DB transaction → dispatcher publishes to Redis Streams → workers consume idempotently (processed-event ids + dead-letter queue). At-least-once delivery everywhere; never assume exactly-once across DB, broker, payment providers, and chain.

**Canonical event envelope:**
```json
{"event_id":"uuid","event_type":"post.viewed","schema_version":1,
 "occurred_at":"2026-10-11T12:00:00Z","aggregate_type":"post","aggregate_id":"uuid",
 "actor_ref":"pseudonymous-id","trace_id":"uuid",
 "payload":{"post_id":"uuid","view_duration_ms":4500,"geo_bucket":"kathmandu","consent_version":"v1"}}
```

**Analytics pipeline** (the engine behind insight assets):
```
Event validation → consent check → bot/fraud filtering → deduplication
  → aggregation (hourly/daily rollups) → privacy gate (cohort ≥30, suppression)
  → snapshot generation → encryption + manifest hashing → asset-ready
```
A manifest hash proves the *recorded dataset* hasn't changed — not that the underlying events were genuine. Bot filtering quality is a disclosed, monitored metric, not a guarantee.

**Visualization spec** (what the owner sees): time-series of attention (hour/day), district/grid heatmap, funnel (impression → view → like → share → comment), top-regions table, all rendered from a versioned JSON spec so the frontend and any export stay consistent.

---

## 14. Infrastructure

### 14.1 Docker Compose topology (skeleton — Dockerfiles, networks, secrets, digests still to be written)

```yaml
services:
  web:        # Next.js PWA
    build: ./apps/web
    depends_on: [api]
  api:        # FastAPI
    build: ./backend
    depends_on:
      postgres: {condition: service_healthy}
      redis: {condition: service_started}
  worker:     # Celery/RQ: outbox dispatch, analytics, notifications
    build: ./backend
    command: celery -A app.worker worker --loglevel=info
    depends_on: [redis, postgres]
  scheduler:  # beat: presence expiry, auction closing, reservation release
    build: ./backend
    command: celery -A app.worker beat --loglevel=info
  postgres:
    image: postgis/postgis:17-3.5
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck: {test: ["CMD-SHELL", "pg_isready -U nexus -d nexus"]}
  redis:
    image: redis:7-alpine
  storage:    # S3-compatible object storage
    image: minio/minio
    command: server /data --console-address ":9001"
    volumes: [object_data:/data]
  routing:    # Valhalla with Nepal OSM extract (PROPOSED)
    build: ./infrastructure/routing
  chain:      # Anvil — only in web3-dev profile
    image: ghcr.io/foundry-rs/foundry
    command: anvil --host 0.0.0.0
    profiles: ["web3-dev"]
volumes: {postgres_data:, object_data:}
```

Standards: multi-stage Dockerfiles, pinned versions + digests, healthchecks, non-root users, env-specific config, secrets via vault/env (never images).

### 14.2 Environments
| Env | Purpose |
|-----|---------|
| Local | Dev workstation, seed data, mock payments, Anvil |
| CI | Lint, migrations, unit/integration/contract tests, image scan |
| Staging | Prod-like, simulated settlement, acceptance tests |
| Production (Nepal) | Fiat settlement, signed provenance log, monitoring, backups |

Separate DBs, buckets, credentials, signing keys per environment.

### 14.3 Pipeline
`Push → static analysis → unit tests → integration tests → build images → security scan → staging deploy → E2E → release approval → production deploy (health-gated, documented rollback; DB rollback planned separately) → monitoring/alerting.`

### 14.4 Nonfunctional targets (proposed, to be benchmarked pre-release under Nepal network conditions)
API 99.5% monthly · read p95 < 500 ms · search p95 < 1 s · realtime msg p95 < 2 s · 1,000 concurrent sessions load test · daily full backups + WAL · RPO 1h / RTO 4h · WCAG 2.2 AA · current Chrome/Firefox/Safari/Edge · structured logs/metrics/traces/alerting.

---

## 15. Testing strategy and release gates

| Layer | Tool | Focus |
|-------|------|-------|
| Python unit | pytest | Domain rules, authz, auction math, privacy gate |
| API integration | pytest + HTTP client | Transactions, API contracts, webhook verification |
| Frontend unit | Vitest | Components, state, validation |
| Browser E2E | Playwright | Full user journeys |
| DB | Migration/SQL tests | Constraints, indexes, PostGIS correctness |
| Load | k6/Locust | Concurrency, latency under Nepal-like conditions |
| Contracts | Foundry | Access control, settlement, invariants, fuzz |
| Security | SAST/DAST/dep scan + pentest | Vulns, misconfig |
| Accessibility | axe + manual | Keyboard, screen reader, contrast |
| Recovery | Drills | Backup restore, RPO/RTO |

**Critical E2E scenarios (must pass before pilot):**
1. **Dating safety:** two adults opt in → discover via bands only → proposal → accept → chat → block → verify zero further contact and zero location disclosure. Adversarial probing (rapid radius changes) yields nothing precise.
2. **Marketplace race:** two buyers, last unit → exactly one order paid, stock never negative, loser sees clean state; review appears only after fulfillment.
3. **Insight asset:** post → events → privacy-gated snapshot → mint → teaser hides full resolution → auction → settle → ownership + KMS policy transfer → old owner gets 403 on full analytics.
4. **Payment failure:** webhook forgery rejected; duplicate webhook doesn't double-grant; failed capture rolls back without partial ownership.
5. **Web3 (simulated):** mint → bid → settle → provenance log reconciles with off-chain manifest.

**Release gates (no public launch unless all hold):** security findings resolved/risk-accepted · payment reconciliation passes failure tests · dating privacy passes adversarial tests · moderation + reporting operational · legal reviews signed off · backups/restore drilled · monitoring + incident escalation live.

---

## 16. Phased roadmap

| Phase | Weeks | Focus | Exit gate |
|-------|-------|-------|-----------|
| 0 | 2–3 | Architecture, repo + Compose, CI, threat model, Nepal legal kickoff | Reproducible local env; approved domain model |
| 1 | 4–6 | Identity/progressive roles, PostGIS migrations, MapLibre shell, guest flows, audit/outbox | Map-first app with guest + auth |
| 2 | 5–8 | Sellers/listings, atomic orders, eSewa/Khalti sandbox, reviews, Valhalla routing + GPS | Testable commerce + navigation |
| 3 | 5–7 | Dating presence/pool/proposals/chat, block/report, adversarial location tests | Safe proposal-to-chat approved for pilot |
| 4 | 6–9 | Posts/media/versioning, engagement pipeline, private Studio analytics, privacy gate | Private creator intelligence verified |
| 5 | 5–8 | **Insight Asset Protocol**: mint, encryption/KMS, teasers, auctions, SettlementAdapter (fiat + simulated), provenance log | End-to-end asset sale with crypto disabled in prod config |
| 6 | 4–6 | Load/security/a11y hardening, recovery drills, pilot onboarding, launch review | Approved, monitored pilot |

**Indicative horizon: 7–12 months** for a small coordinated team (some parallel phases). A solo developer: substantially longer. Dating + commerce + asset pilots also need moderation/support staffing.

**Suggested team:** 1 product/architect · 1–2 frontend · 1–2 backend/geo · part-time contract engineer · part-time designer · part-time QA/security (ramping pre-launch) · external Nepal legal counsel · moderation/support before public dating/commerce.

### Sprint 1–2 backlog
- [ ] NX-001 (P0) Monorepo + Docker Compose skeleton (web/api/worker/postgres/redis/storage)
- [ ] NX-002 (P0) PostGIS migrations: identity + presence + listings + posts tables
- [ ] NX-003 (P0) Next.js shell: nav, route inventory, design tokens, PWA manifest
- [ ] NX-004 (P0) FastAPI: health, auth, RFC-7807 errors, session/guest model
- [ ] NX-005 (P0) Guest + registration flows; progressive role grants
- [ ] NX-006 (P0) MapLibre interface + spatial search endpoint
- [ ] NX-007 (P0) Consent model + data-classification doc
- [ ] NX-008 (P0) Structured logging + audit + outbox dispatcher
- [ ] NX-009 (P1) Marketplace listing CRUD
- [ ] NX-010 (P0) CI: tests + container/dependency scanning
- [ ] NX-011 (P0) SettlementAdapter skeleton (Fiat/Simulated/Onchain) + config policy
- [ ] NX-012 (P1) Valhalla spike: Nepal extract → sample route

---

## 17. Decisions register, open questions, risks

### ADR (abridged)
| ID | Decision | Status |
|----|----------|--------|
| ADR-001 | Modular monolith (FastAPI), selectively separated infra | Confirmed |
| ADR-002 | Next.js responsive PWA, no native apps for MVP | Confirmed |
| ADR-003 | PostgreSQL/PostGIS as system of record | Confirmed |
| ADR-004 | MapLibre GL for map UI | Confirmed |
| ADR-005 | Redis Streams for event transport; Celery workers | Confirmed |
| ADR-006 | Private analytics + payloads off-chain, encrypted | Required boundary |
| ADR-007 | Insight assets transfer **ownership** (sale); copyright never moves | Confirmed product direction |
| ADR-008 | Transfer-restricted ERC-721; settlement only via platform contracts/adapters | Confirmed |
| ADR-009 | EVM-compatible, no proprietary token in MVP | Confirmed |
| ADR-010 | Crypto settlement **disabled** in Nepal production (NRB notice) | Legal gate |
| ADR-011 | eSewa/Khalti fiat rail; server-verified webhooks only | Confirmed |
| ADR-012 | Kathmandu Valley pilot geography | Proposed |
| ADR-013 | English first, Nepali i18n designed in | Proposed |
| ADR-014 | Valhalla self-hosted routing, Nepal OSM extract | Proposed |
| ADR-015 | Custodial KMS with owner-bound policy (owner-held keys later) | Proposed |
| ADR-016 | 18+ dating, bands+jitter+TTL anti-triangulation | Required safety baseline |
| ADR-017 | Platform fee PROPOSED 5% on auction settlement | Proposed |

### Open questions
1. Exact pilot geography and launch business categories.
2. eSewa/Khalti merchant onboarding + **pre-auth/hold capability** (decides bid-escrow UX in fiat mode).
3. Public chain selection for the future cleared jurisdiction (fees, finality, wallet support in Nepal).
4. Moderation/support staffing and SLAs before dating/commerce pilot.
5. Platform fee % and creator payout schedule.
6. KMS choice and acceptance of the custodial trust model.
7. Legal clearance path (if ever) for on-chain settlement in Nepal.
8. Bid-escrow fallback design if providers lack holds ("binding offer + 24h capture").
9. Valuation guidance: how do creators price insight assets? (Marketplace needs comps/education.)
10. Dispute resolution for auctions (non-paying winner → next-highest-bidder flow).

### Top risks
- **Regulatory:** crypto-adjacent product in a restrictive jurisdiction — mitigated by fiat-first + signed provenance, but legal review is the critical path.
- **Safety:** dating location abuse — mitigated by design (§12.1), must be adversarially tested.
- **Trust:** insight assets are only as credible as bot filtering — disclose methodology, monitor, never overclaim.
- **Cold start:** five modules need liquidity (daters, sellers, creators, bidders) — pilot sequencing matters more than code.

---

## 18. What to build first

Not the smart contract. Not the dating pool. Build the foundation:

1. Docker environment + monorepo + CI.
2. Next.js shell with final navigation + design tokens.
3. FastAPI with auth, guest sessions, permissions, error conventions.
4. PostgreSQL/PostGIS migrations (identity → geo → commerce → creator → assets).
5. Guest browsing + public geographic discovery on the map.
6. Outbox + audit + structured logging.
7. SettlementAdapter skeleton with the Nepal `FIAT`-default policy.

Then modules stack without rework: marketplace → dating → creator analytics → **Insight Asset Protocol** → hardening → pilot.

**Final position:** NEXUS is a location-aware Web2 application with a Web3 ownership spine. The chain proves *who owns which insight* and *that it hasn't been altered* — it never holds people's locations, messages, or audiences. That is what makes the concept both ambitious and shippable in Nepal.

---
*End of NEXUS v2.0 — Complete Platform Design.*
