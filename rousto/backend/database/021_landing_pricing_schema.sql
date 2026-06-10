-- Rousto — Landing page & pricing schema
-- See docs/14_LANDING_PAGE_PRICING.md

CREATE TABLE landing_hero_stats (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        VARCHAR(40) NOT NULL UNIQUE,
    value_ar    VARCHAR(40) NOT NULL,
    label_ar    VARCHAR(80) NOT NULL,
    sort_order  SMALLINT NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE landing_pricing_plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    name_ar         VARCHAR(80) NOT NULL,
    description_ar  VARCHAR(300),
    price_sar       NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (price_sar >= 0),
    price_label_ar  VARCHAR(60) NOT NULL DEFAULT 'شهرياً',
    billing_period  VARCHAR(20) NOT NULL DEFAULT 'monthly',
    features        JSONB NOT NULL DEFAULT '[]'::jsonb,
    cta_text_ar     VARCHAR(60) NOT NULL DEFAULT 'ابدأ الآن',
    cta_url         VARCHAR(200),
    badge_ar        VARCHAR(40),
    is_featured     BOOLEAN NOT NULL DEFAULT false,
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE landing_page_features (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    title_ar        VARCHAR(120) NOT NULL,
    description_ar  VARCHAR(300),
    icon_key        VARCHAR(40),
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX idx_landing_hero_stats_active ON landing_hero_stats(is_active, sort_order);
CREATE INDEX idx_landing_pricing_plans_active ON landing_pricing_plans(is_active, sort_order);
CREATE INDEX idx_landing_page_features_active ON landing_page_features(is_active, sort_order);
