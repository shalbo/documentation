-- Rousto — English translations for catalog and dynamic content

UPDATE service_categories SET name_en = CASE slug
    WHEN 'all' THEN 'All'
    WHEN 'oil' THEN 'Oil'
    WHEN 'tires' THEN 'Tires'
    WHEN 'brakes' THEN 'Brakes'
    WHEN 'ac' THEN 'A/C'
    WHEN 'electrical' THEN 'Electrical'
    ELSE name_en
END;

UPDATE services SET
    name_en = CASE slug
        WHEN 'oil-change' THEN 'Oil & Filter Change'
        WHEN 'tires' THEN 'Tires & Balancing'
        WHEN 'brakes' THEN 'Brake System Service'
        WHEN 'ac' THEN 'A/C & Cooling'
        WHEN 'battery' THEN 'Battery & Electrical'
        WHEN 'diagnostics' THEN 'Full Computer Diagnostics'
        ELSE name_en
    END,
    subtitle_en = CASE slug
        WHEN 'oil-change' THEN 'OEM oil + full inspection'
        WHEN 'tires' THEN 'Balancing and tire replacement'
        WHEN 'brakes' THEN 'Pads inspection and replacement'
        WHEN 'ac' THEN 'Freon refill and maintenance'
        WHEN 'battery' THEN 'Battery test and installation'
        WHEN 'diagnostics' THEN 'Precise electronic diagnostics'
        ELSE subtitle_en
    END;

UPDATE promotions SET
    title_en = CASE code
        WHEN 'ROUSTO' THEN '25% off your first booking'
        WHEN 'GOLD2026' THEN 'Gold maintenance package'
        ELSE title_en
    END,
    description_en = CASE code
        WHEN 'ROUSTO' THEN 'Use code ROUSTO at checkout'
        WHEN 'GOLD2026' THEN 'Save up to SAR 120 per year'
        ELSE description_en
    END;

UPDATE payment_methods SET label_en = 'Mada **** 4421'
WHERE id = 'd0000000-0000-4000-8000-000000000001';

UPDATE notification_templates SET
    title_template_en = CASE slug
        WHEN 'booking_status' THEN 'Booking update {{reference}}'
        WHEN 'support_reply' THEN 'Reply to ticket {{reference}}'
        WHEN 'towing_status' THEN 'Towing update {{reference}}'
        WHEN 'promo_offer' THEN '{{title}}'
        WHEN 'security_alert' THEN 'Security alert'
        WHEN 'system_announcement' THEN '{{title}}'
        ELSE title_template_en
    END,
    body_template_en = CASE slug
        WHEN 'booking_status' THEN '{{label}}'
        WHEN 'support_reply' THEN '{{preview}}'
        WHEN 'towing_status' THEN '{{label}}'
        WHEN 'promo_offer' THEN '{{body}}'
        WHEN 'security_alert' THEN '{{message}}'
        WHEN 'system_announcement' THEN '{{body}}'
        ELSE body_template_en
    END;

UPDATE support_faq SET
    question_en = 'How do I track my technician?',
    answer_en = 'Open the Tracking tab or Delivery Map to see live ETA and status updates.'
WHERE slug = 'track-technician';

UPDATE support_faq SET
    question_en = 'What payment methods are supported?',
    answer_en = 'We support Mada, Apple Pay, Visa, and Mastercard.'
WHERE slug = 'payment-methods';
