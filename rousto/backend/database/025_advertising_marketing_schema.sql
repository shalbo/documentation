-- Rousto — Advertising & Marketing schema
-- See docs/18_ADVERTISING_AND_MARKETING_MODULE.md

CREATE TABLE marketing_campaigns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    name_ar         VARCHAR(120) NOT NULL,
    description_ar  VARCHAR(300),
    channel         VARCHAR(30) NOT NULL DEFAULT 'web',
    utm_source      VARCHAR(60),
    utm_medium      VARCHAR(60),
    utm_campaign    VARCHAR(60),
    utm_content     VARCHAR(60),
    starts_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    ends_at         TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE marketing_banners (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    title_ar        VARCHAR(120) NOT NULL,
    subtitle_ar     VARCHAR(200),
    placement       VARCHAR(30) NOT NULL,
    image_url       VARCHAR(300),
    cta_text_ar     VARCHAR(60),
    cta_url         VARCHAR(200),
    campaign_id     UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    promotion_id    UUID REFERENCES promotions(id) ON DELETE SET NULL,
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    starts_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    ends_at         TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE marketing_partners (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    name_ar         VARCHAR(80) NOT NULL,
    logo_url        VARCHAR(300),
    website_url     VARCHAR(200),
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE marketing_newsletter_subscribers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    source          VARCHAR(40) NOT NULL DEFAULT 'landing',
    campaign_id     UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    subscribed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    unsubscribed_at TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE marketing_referrals (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code             VARCHAR(20) NOT NULL UNIQUE,
    reward_points    INTEGER NOT NULL DEFAULT 100,
    max_uses         SMALLINT,
    uses_count       INTEGER NOT NULL DEFAULT 0,
    is_active        BOOLEAN NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE marketing_referral_events (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id      UUID NOT NULL REFERENCES marketing_referrals(id) ON DELETE CASCADE,
    referred_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    booking_id       UUID REFERENCES bookings(id) ON DELETE SET NULL,
    reward_granted   BOOLEAN NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE marketing_attribution_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id     UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    event_type      VARCHAR(30) NOT NULL,
    utm_source      VARCHAR(60),
    utm_medium      VARCHAR(60),
    utm_campaign    VARCHAR(60),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id      VARCHAR(64),
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_marketing_banners_active ON marketing_banners(is_active, placement, sort_order);
CREATE INDEX idx_marketing_campaigns_active ON marketing_campaigns(is_active, starts_at);
CREATE INDEX idx_marketing_partners_active ON marketing_partners(is_active, sort_order);
CREATE INDEX idx_marketing_attribution_created ON marketing_attribution_events(created_at DESC);
