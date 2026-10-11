"""Initial schema — NEXUS core tables (design §8).

Revision ID: 0001
Revises: None
Create Date: 2026-10-11
"""
from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

DDL = """
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- ============ IDENTITY ============
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email CITEXT UNIQUE,
    phone TEXT UNIQUE,
    password_hash TEXT,
    date_of_birth DATE,
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
    avatar_key TEXT,
    visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (visibility IN ('public','private'))
);

CREATE TABLE user_preferences (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    settings_json JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (user_id, category)
);

CREATE TABLE user_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,
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

CREATE TABLE blocks (
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
    meeting_area TEXT,
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
    body_ciphertext TEXT NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_conv_time ON messages (conversation_id, sent_at);

-- ============ MARKETPLACE ============
CREATE TABLE sellers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id),
    type TEXT NOT NULL CHECK (type IN ('individual','store')),
    display_name TEXT NOT NULL,
    slug TEXT UNIQUE,
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
    currency TEXT NOT NULL DEFAULT 'NPR' CHECK (currency = 'NPR'),
    location GEOGRAPHY(Point, 4326) NOT NULL,
    location_label TEXT NOT NULL,
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
    expires_at TIMESTAMPTZ NOT NULL,
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
    auction_id UUID,
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
    order_id UUID NOT NULL UNIQUE REFERENCES orders(id),
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
    content_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (post_id, version)
);

CREATE TABLE engagement_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    actor_ref TEXT NOT NULL,
    event_type TEXT NOT NULL
        CHECK (event_type IN ('impression','view','like','share','comment','click')),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    geo_bucket TEXT NOT NULL,
    consent_ref TEXT NOT NULL,
    view_duration_ms INTEGER
);
CREATE INDEX idx_eng_post_time ON engagement_events (post_id, occurred_at DESC);

-- ============ INSIGHT ASSETS ============
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    manifest_hash TEXT NOT NULL,
    object_key TEXT NOT NULL,
    dek_ref TEXT NOT NULL,
    privacy_report JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'ready' CHECK (status IN ('ready','superseded')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (window_end > window_start)
);

CREATE TABLE insight_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES analytics_snapshots(id),
    post_id UUID NOT NULL REFERENCES posts(id),
    creator_id UUID NOT NULL REFERENCES users(id),
    owner_id UUID NOT NULL REFERENCES users(id),
    chain_id BIGINT,
    token_address TEXT,
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
    tx_hash TEXT,
    registry_signature TEXT,
    transferred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE entitlements (
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
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,
    meta JSONB NOT NULL DEFAULT '{}',
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_actor_time ON audit_events (actor_id, occurred_at DESC);
CREATE INDEX idx_audit_resource ON audit_events (resource_type, resource_id);

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id UUID NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);
CREATE INDEX idx_outbox_unpublished ON outbox_events (created_at) WHERE published_at IS NULL;

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id),
    target_type TEXT NOT NULL CHECK (target_type IN ('user','post','listing','message','asset')),
    target_id UUID NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','reviewing','actioned','dismissed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def upgrade() -> None:
    op.execute(DDL)


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS reports, outbox_events, audit_events, entitlements,
            ownership_transfers, bids, auctions, insight_assets, analytics_snapshots,
            engagement_events, post_versions, posts, reviews, payments, order_items,
            orders, inventory_reservations, listings, products, sellers, messages,
            conversations, date_proposals, date_presence, date_profiles, blocks,
            wallet_links, user_consents, user_preferences, profiles, users CASCADE;
        """
    )
