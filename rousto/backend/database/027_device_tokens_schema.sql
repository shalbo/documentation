-- Rousto — FCM device tokens for push notifications

CREATE TABLE user_device_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fcm_token   VARCHAR(512) NOT NULL,
    platform    VARCHAR(20) NOT NULL DEFAULT 'unknown',
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, fcm_token)
);

CREATE INDEX idx_user_device_tokens_user ON user_device_tokens(user_id) WHERE is_active = true;
