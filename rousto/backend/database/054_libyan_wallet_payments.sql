-- Libyan local payments & in-app wallets (LYD only — no international gateways)

ALTER TABLE tiers
    ADD COLUMN IF NOT EXISTS platform_commission_rate NUMERIC(5, 4) NOT NULL DEFAULT 0.1500
        CHECK (platform_commission_rate >= 0 AND platform_commission_rate <= 1);

CREATE TABLE IF NOT EXISTS wallets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_type      VARCHAR(20) NOT NULL
                    CHECK (owner_type IN ('customer', 'vendor', 'driver', 'platform')),
    owner_id        UUID NOT NULL,
    balance_lyd     NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (balance_lyd >= 0),
    pending_lyd     NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (pending_lyd >= 0),
    currency        VARCHAR(3) NOT NULL DEFAULT 'LYD' CHECK (currency = 'LYD'),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (owner_type, owner_id)
);

CREATE INDEX IF NOT EXISTS idx_wallets_owner ON wallets (owner_type, owner_id);

CREATE TABLE IF NOT EXISTS wallet_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id           UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    amount_lyd          NUMERIC(12, 2) NOT NULL CHECK (amount_lyd > 0),
    direction           VARCHAR(10) NOT NULL CHECK (direction IN ('credit', 'debit')),
    transaction_type    VARCHAR(20) NOT NULL
                        CHECK (transaction_type IN ('deposit', 'withdraw', 'payment', 'commission', 'refund', 'payout')),
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'completed', 'failed')),
    reference_type      VARCHAR(40),
    reference_id        UUID,
    gateway             VARCHAR(20)
                        CHECK (gateway IS NULL OR gateway IN ('cod', 'wallet', 'muamalat', 'sadad', 'edfali')),
    gateway_ref         VARCHAR(120),
    description_ar      VARCHAR(300),
    metadata            JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_wallet_tx_wallet ON wallet_transactions (wallet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wallet_tx_status ON wallet_transactions (status);

CREATE TABLE IF NOT EXISTS withdrawal_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id       UUID NOT NULL REFERENCES wallets(id),
    vendor_id       UUID NOT NULL REFERENCES vendors(id),
    amount_lyd      NUMERIC(12, 2) NOT NULL CHECK (amount_lyd > 0),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'rejected', 'paid')),
    bank_name       VARCHAR(80),
    iban            VARCHAR(34),
    note            TEXT,
    admin_note      TEXT,
    approved_by     VARCHAR(80),
    paid_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_withdrawal_vendor ON withdrawal_requests (vendor_id, status);

CREATE TABLE IF NOT EXISTS gateway_payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    amount_lyd      NUMERIC(12, 2) NOT NULL CHECK (amount_lyd > 0),
    gateway         VARCHAR(20) NOT NULL
                    CHECK (gateway IN ('cod', 'wallet', 'muamalat', 'sadad', 'edfali')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'redirected', 'completed', 'failed', 'cancelled')),
    order_type      VARCHAR(40) NOT NULL,
    order_id        UUID,
    redirect_url    TEXT,
    gateway_ref     VARCHAR(120),
    signature_hash  VARCHAR(128),
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gateway_payments_user ON gateway_payments (user_id);
CREATE INDEX IF NOT EXISTS idx_gateway_payments_ref ON gateway_payments (gateway_ref);
CREATE INDEX IF NOT EXISTS idx_gateway_payments_status ON gateway_payments (status);

CREATE TABLE IF NOT EXISTS payment_audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      VARCHAR(60) NOT NULL,
    gateway         VARCHAR(20),
    reference_id    UUID,
    ip_address      VARCHAR(45),
    payload_hash    VARCHAR(64),
    details         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_payment_audit_created ON payment_audit_logs (created_at DESC);
