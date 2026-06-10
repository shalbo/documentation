-- Rousto — customer support & security

CREATE TABLE support_faq (
    id           UUID PRIMARY KEY,
    slug         VARCHAR(60) NOT NULL UNIQUE,
    category     VARCHAR(40) NOT NULL,
    question_ar  VARCHAR(300) NOT NULL,
    answer_ar    TEXT NOT NULL,
    sort_order   SMALLINT NOT NULL DEFAULT 0,
    is_active    BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE support_tickets (
    id           UUID PRIMARY KEY,
    reference    VARCHAR(12) NOT NULL UNIQUE,
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    booking_id   UUID REFERENCES bookings(id) ON DELETE SET NULL,
    category     VARCHAR(40) NOT NULL
                 CHECK (category IN ('booking', 'payment', 'account', 'technical', 'other')),
    priority     VARCHAR(20) NOT NULL DEFAULT 'normal'
                 CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status       VARCHAR(30) NOT NULL DEFAULT 'open'
                 CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')),
    subject      VARCHAR(200) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at  TIMESTAMPTZ
);

CREATE INDEX idx_support_tickets_user ON support_tickets (user_id, created_at DESC);
CREATE INDEX idx_support_tickets_status ON support_tickets (status, priority, created_at DESC);

CREATE TABLE support_ticket_messages (
    id            UUID PRIMARY KEY,
    ticket_id     UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    author_type   VARCHAR(20) NOT NULL CHECK (author_type IN ('customer', 'admin', 'system')),
    author_label  VARCHAR(80) NOT NULL,
    message       TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_support_messages_ticket ON support_ticket_messages (ticket_id, created_at);

CREATE TABLE security_audit_logs (
    id           UUID PRIMARY KEY,
    user_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type   VARCHAR(60) NOT NULL,
    severity     VARCHAR(20) NOT NULL DEFAULT 'info'
                 CHECK (severity IN ('info', 'warn', 'critical')),
    ip_address   VARCHAR(45),
    user_agent   VARCHAR(300),
    metadata     JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_security_audit_user ON security_audit_logs (user_id, created_at DESC);
CREATE INDEX idx_security_audit_type ON security_audit_logs (event_type, created_at DESC);

CREATE TABLE user_security_profiles (
    user_id                          UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    login_alerts_enabled             BOOLEAN NOT NULL DEFAULT true,
    suspicious_activity_reported_at  TIMESTAMPTZ,
    last_security_review_at          TIMESTAMPTZ,
    updated_at                       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
