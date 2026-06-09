-- Rousto — Centralized Notification Engine: dispatch log + broadcasts

CREATE TABLE notification_dispatch_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_source        VARCHAR(60) NOT NULL,
    notification_id     UUID REFERENCES notifications(id) ON DELETE SET NULL,
    broadcast_id        UUID,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category            VARCHAR(30) NOT NULL,
    template_slug       VARCHAR(60),
    title               VARCHAR(200) NOT NULL,
    channel             VARCHAR(20) NOT NULL DEFAULT 'both',
    push_sent           BOOLEAN NOT NULL DEFAULT false,
    in_app_created      BOOLEAN NOT NULL DEFAULT false,
    status              VARCHAR(20) NOT NULL DEFAULT 'delivered',
    metadata_json       JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_dispatch_log_created ON notification_dispatch_log(created_at DESC);
CREATE INDEX idx_dispatch_log_user ON notification_dispatch_log(user_id, created_at DESC);
CREATE INDEX idx_dispatch_log_source ON notification_dispatch_log(event_source);

CREATE TABLE notification_broadcasts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference           VARCHAR(20) NOT NULL UNIQUE,
    category            VARCHAR(30) NOT NULL,
    title               VARCHAR(200) NOT NULL,
    body                TEXT NOT NULL,
    target_segment      VARCHAR(40) NOT NULL,
    template_slug       VARCHAR(60),
    recipients_count    INTEGER NOT NULL DEFAULT 0,
    push_sent_count     INTEGER NOT NULL DEFAULT 0,
    in_app_count        INTEGER NOT NULL DEFAULT 0,
    skipped_count       INTEGER NOT NULL DEFAULT 0,
    created_by          VARCHAR(120),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE notification_dispatch_log
    ADD CONSTRAINT fk_dispatch_broadcast
    FOREIGN KEY (broadcast_id) REFERENCES notification_broadcasts(id) ON DELETE SET NULL;
