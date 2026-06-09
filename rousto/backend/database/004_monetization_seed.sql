-- Rousto — monetization seed data

INSERT INTO membership_plans (id, slug, name_ar, description_ar, price_sar, billing_period, discount_percent, priority_booking, free_inspection, sort_order) VALUES
    ('m0000000-0000-4000-8000-000000000001', 'free', 'مجاني',
     'الخطة الأساسية — احجز وادفع لكل خدمة', 0, 'monthly', 0, false, false, 0),
    ('m0000000-0000-4000-8000-000000000002', 'gold', 'ذهبي',
     'خصم 10٪ على كل خدمة + أولوية الحجز', 29, 'monthly', 10, true, false, 1),
    ('m0000000-0000-4000-8000-000000000003', 'platinum', 'بلاتيني',
     'خصم 20٪ + فحص مجاني سنوي + أولوية قصوى', 79, 'monthly', 20, true, true, 2);

INSERT INTO service_packages (id, slug, name_ar, description_ar, price_sar, visits_count, validity_days, savings_sar) VALUES
    ('p0000000-0000-4000-8000-000000000001', 'gold-maintenance', 'باقة الصيانة الذهبية',
     '4 زيارات صيانة سنوية — زيت + فحص + إطارات', 499, 4, 365, 120),
    ('p0000000-0000-4000-8000-000000000002', 'basic-care', 'باقة العناية الأساسية',
     'زيت + فحص شامل — زيارتان', 199, 2, 180, 40);

INSERT INTO package_items (package_id, service_id, quantity) VALUES
    ('p0000000-0000-4000-8000-000000000001', 'f0000000-0000-4000-8000-000000000001', 2),
    ('p0000000-0000-4000-8000-000000000001', 'f0000000-0000-4000-8000-000000000006', 1),
    ('p0000000-0000-4000-8000-000000000001', 'f0000000-0000-4000-8000-000000000002', 1),
    ('p0000000-0000-4000-8000-000000000002', 'f0000000-0000-4000-8000-000000000001', 1),
    ('p0000000-0000-4000-8000-000000000002', 'f0000000-0000-4000-8000-000000000006', 1);

INSERT INTO loyalty_rewards (id, slug, title_ar, description_ar, points_cost, discount_sar) VALUES
    ('r0000000-0000-4000-8000-000000000001', 'discount-10', 'خصم 10 ريال',
     'استبدل 100 نقطة بخصم 10 ريال على خدمتك القادمة', 100, 10),
    ('r0000000-0000-4000-8000-000000000002', 'discount-30', 'خصم 30 ريال',
     'استبدل 300 نقطة بخصم 30 ريال', 300, 30),
    ('r0000000-0000-4000-8000-000000000003', 'free-inspection', 'فحص مجاني',
     'استبدل 500 نقطة بفحص كمبيوتر مجاني', 500, 75);

-- Revenue split for existing booking
INSERT INTO booking_revenue (
    booking_id, gross_sar, membership_discount_sar, promo_discount_sar,
    points_discount_sar, net_sar, platform_fee_sar, technician_payout_sar, reserve_sar
) VALUES (
    'i0000000-0000-4000-8000-000000000001',
    120.00, 0, 30.00, 0, 90.00, 13.50, 67.50, 9.00
);

INSERT INTO promotion_redemptions (user_id, promotion_id, booking_id, discount_sar)
VALUES (
    'a0000000-0000-4000-8000-000000000001',
    'h0000000-0000-4000-8000-000000000001',
    'i0000000-0000-4000-8000-000000000001',
    30.00
);
