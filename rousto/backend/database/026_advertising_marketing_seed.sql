-- Rousto — Advertising & Marketing seed data

INSERT INTO permissions (id, slug, name_ar, resource, action) VALUES
    ('p0000000-0000-4000-8000-000000000018', 'marketing:read', 'قراءة التسويق', 'marketing', 'read'),
    ('p0000000-0000-4000-8000-000000000019', 'marketing:manage', 'إدارة التسويق', 'marketing', 'manage'),
    ('p0000000-0000-4000-8000-000000000020', 'promotions:manage', 'إدارة العروض', 'promotions', 'manage'),
    ('p0000000-0000-4000-8000-000000000021', 'testimonials:manage', 'إدارة آراء العملاء', 'testimonials', 'manage'),
    ('p0000000-0000-4000-8000-000000000022', 'newsletter:manage', 'إدارة النشرة', 'newsletter', 'manage')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000001', id FROM permissions
WHERE slug IN ('marketing:read')
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000002', id FROM permissions
WHERE slug IN ('marketing:read', 'marketing:manage', 'promotions:manage', 'testimonials:manage', 'newsletter:manage')
ON CONFLICT DO NOTHING;

INSERT INTO marketing_campaigns (id, slug, name_ar, description_ar, channel, utm_source, utm_medium, utm_campaign) VALUES
    ('mc000000-0000-4000-8000-000000000001', 'summer-2026', 'حملة الصيف 2026', 'خصومات صيانة الصيف', 'web', 'rousto', 'landing', 'summer-2026'),
    ('mc000000-0000-4000-8000-000000000002', 'app-launch', 'إطلاق التطبيق', 'عروض حصرية لمستخدمي التطبيق', 'app', 'rousto', 'app', 'app-launch');

INSERT INTO marketing_banners (id, slug, title_ar, subtitle_ar, placement, cta_text_ar, cta_url, campaign_id, promotion_id, sort_order) VALUES
    ('mb000000-0000-4000-8000-000000000001', 'hero-summer', 'صيانة صيفية بخصم 25٪', 'احجز الآن واستفد من عرض الصيف', 'home_hero', 'احجز بخصم', '#booking', 'mc000000-0000-4000-8000-000000000001', NULL, 0),
    ('mb000000-0000-4000-8000-000000000002', 'booking-rousto', 'كود ROUSTO — خصم أول حجز', 'طبّق الكود عند الدفع', 'booking', 'تطبيق الكود', '#booking', 'mc000000-0000-4000-8000-000000000001', (SELECT id FROM promotions WHERE code = 'ROUSTO' LIMIT 1), 0);

INSERT INTO marketing_partners (id, slug, name_ar, sort_order) VALUES
    ('mp000000-0000-4000-8000-000000000001', 'toyota', 'تويوتا', 1),
    ('mp000000-0000-4000-8000-000000000002', 'hyundai', 'هيونداي', 2),
    ('mp000000-0000-4000-8000-000000000003', 'nissan', 'نيسان', 3),
    ('mp000000-0000-4000-8000-000000000004', 'kia', 'كيا', 4),
    ('mp000000-0000-4000-8000-000000000005', 'ford', 'فورد', 5),
    ('mp000000-0000-4000-8000-000000000006', 'bmw', 'بي إم دبليو', 6),
    ('mp000000-0000-4000-8000-000000000007', 'mercedes', 'مرسيدس', 7);

INSERT INTO marketing_newsletter_subscribers (id, email, source, campaign_id) VALUES
    ('mn000000-0000-4000-8000-000000000001', 'demo@rousto.sa', 'landing', 'mc000000-0000-4000-8000-000000000001');

INSERT INTO marketing_referrals (id, referrer_user_id, code, reward_points, max_uses) VALUES
    ('mr000000-0000-4000-8000-000000000001', 'a0000000-0000-4000-8000-000000000001', 'SAUD100', 100, 50);

INSERT INTO marketing_attribution_events (id, campaign_id, event_type, utm_source, utm_medium, utm_campaign, session_id) VALUES
    ('ma000000-0000-4000-8000-000000000001', 'mc000000-0000-4000-8000-000000000001', 'page_view', 'rousto', 'landing', 'summer-2026', 'demo-session-001');
