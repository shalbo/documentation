-- Rousto — Landing page & pricing seed data

INSERT INTO landing_hero_stats (id, slug, value_ar, label_ar, sort_order) VALUES
    ('lp000000-0000-4000-8000-000000000001', 'happy_customers', '+25K', 'عميل سعيد', 0),
    ('lp000000-0000-4000-8000-000000000002', 'rating', '4.9★', 'تقييم المتجر', 1),
    ('lp000000-0000-4000-8000-000000000003', 'service_centers', '+120', 'مركز خدمة', 2),
    ('lp000000-0000-4000-8000-000000000004', 'technicians', '+500', 'فني معتمد', 3);

INSERT INTO landing_pricing_plans (
    id, slug, name_ar, description_ar, price_sar, price_label_ar, billing_period,
    features, cta_text_ar, cta_url, badge_ar, is_featured, sort_order
) VALUES
    (
        'lp000000-0000-4000-8000-000000000011',
        'individual',
        'فردي',
        'ادفع لكل خدمة — بدون التزام شهري',
        0,
        'ادفع لكل خدمة',
        'per_visit',
        '["أسعار شفافة لكل خدمة", "حجز فوري بدون اشتراك", "نقاط ولاء على كل زيارة"]'::jsonb,
        'احجز خدمتك',
        '#booking',
        NULL,
        false,
        0
    ),
    (
        'lp000000-0000-4000-8000-000000000012',
        'family',
        'عائلي',
        'مثالي للعائلات — خصم و أولوية حجز',
        29,
        'شهرياً',
        'monthly',
        '["خصم 10٪ على كل خدمة", "أولوية في الحجز", "دعم عملاء مخصص", "نقاط ولاء مضاعفة"]'::jsonb,
        'اشترك الآن',
        '#booking',
        'الأكثر شعبية',
        true,
        1
    ),
    (
        'lp000000-0000-4000-8000-000000000013',
        'business',
        'أعمال',
        'للأساطيل والشركات — خصم أقصى وفحص مجاني',
        79,
        'شهرياً',
        'monthly',
        '["خصم 20٪ على كل خدمة", "فحص كمبيوتر مجاني سنوي", "أولوية قصوى", "تقارير صيانة شهرية", "مدير حساب مخصص"]'::jsonb,
        'تواصل معنا',
        'support.html',
        NULL,
        false,
        2
    );

INSERT INTO landing_page_features (id, slug, title_ar, description_ar, icon_key, sort_order) VALUES
    ('lp000000-0000-4000-8000-000000000021', 'transparent-pricing',
     'أسعار ثابتة وواضحة', 'تعرف على التكلفة قبل تأكيد الحجز.', 'price_check', 0),
    ('lp000000-0000-4000-8000-000000000022', 'certified-techs',
     'فنيون معتمدون', 'فريق مدرّب وحاصل على شهادات معتمدة.', 'verified', 1),
    ('lp000000-0000-4000-8000-000000000023', 'genuine-parts',
     'قطع غيار أصلية', 'ضمان 6 أشهر على كل قطعة.', 'shield', 2),
    ('lp000000-0000-4000-8000-000000000024', 'live-tracking',
     'تتبّع مباشر', 'إشعارات فورية لكل مرحلة من الخدمة.', 'location', 3);
