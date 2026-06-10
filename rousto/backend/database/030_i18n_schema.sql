-- Rousto — bilingual content columns (Arabic + English)

ALTER TABLE service_categories
    ADD COLUMN IF NOT EXISTS name_en VARCHAR(80);

ALTER TABLE services
    ADD COLUMN IF NOT EXISTS name_en VARCHAR(120),
    ADD COLUMN IF NOT EXISTS subtitle_en VARCHAR(200);

ALTER TABLE promotions
    ADD COLUMN IF NOT EXISTS title_en VARCHAR(120),
    ADD COLUMN IF NOT EXISTS description_en VARCHAR(300);

ALTER TABLE payment_methods
    ADD COLUMN IF NOT EXISTS label_en VARCHAR(60);

ALTER TABLE support_faq
    ADD COLUMN IF NOT EXISTS question_en VARCHAR(300),
    ADD COLUMN IF NOT EXISTS answer_en TEXT;

ALTER TABLE notification_templates
    ADD COLUMN IF NOT EXISTS title_template_en VARCHAR(200),
    ADD COLUMN IF NOT EXISTS body_template_en TEXT;

ALTER TABLE membership_plans
    ADD COLUMN IF NOT EXISTS name_en VARCHAR(80),
    ADD COLUMN IF NOT EXISTS description_en VARCHAR(300);

ALTER TABLE loyalty_rewards
    ADD COLUMN IF NOT EXISTS title_en VARCHAR(120),
    ADD COLUMN IF NOT EXISTS description_en VARCHAR(300);

ALTER TABLE marketing_banners
    ADD COLUMN IF NOT EXISTS title_en VARCHAR(120),
    ADD COLUMN IF NOT EXISTS subtitle_en VARCHAR(200),
    ADD COLUMN IF NOT EXISTS cta_text_en VARCHAR(60);
