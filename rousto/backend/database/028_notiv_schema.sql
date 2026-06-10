-- Rousto — NOTIV: in-app notifications, templates, preferences

CREATE TABLE notification_templates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug                VARCHAR(60) NOT NULL UNIQUE,
    category            VARCHAR(30) NOT NULL,
    title_template      VARCHAR(200) NOT NULL,
    body_template       TEXT NOT NULL,
    action_url_template VARCHAR(300),
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_notification_preferences (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category        VARCHAR(30) NOT NULL,
    push_enabled    BOOLEAN NOT NULL DEFAULT true,
    in_app_enabled  BOOLEAN NOT NULL DEFAULT true,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, category)
);

CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category        VARCHAR(30) NOT NULL,
    template_slug   VARCHAR(60),
    title           VARCHAR(200) NOT NULL,
    body            TEXT NOT NULL,
    data_json       JSONB NOT NULL DEFAULT '{}',
    action_url      VARCHAR(300),
    is_read         BOOLEAN NOT NULL DEFAULT false,
    read_at         TIMESTAMPTZ,
    push_sent       BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id) WHERE is_read = false;
