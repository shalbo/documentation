-- Approved vendor linked to seed technician أحمد الفني

INSERT INTO vendors (
    id, business_name, contact_name, email, phone, city,
    status, technician_id, approved_at, approved_by
) VALUES (
    'v0000000-0000-4000-8000-000000000001',
    'خدمات أحمد للسيارات',
    'أحمد الفني',
    'ahmad.vendor@example.com',
    '+966509876543',
    'الرياض',
    'approved',
    'g0000000-0000-4000-8000-000000000001',
    NOW() - INTERVAL '30 days',
    'admin'
);

INSERT INTO vendor_bank_accounts (
    id, vendor_id, bank_name, account_holder, iban, is_primary, is_verified
) VALUES (
    'vb000000-0000-4000-8000-000000000001',
    'v0000000-0000-4000-8000-000000000001',
    'البنك الأهلي',
    'أحمد الفني',
    'SA0380000000608010167519',
    true,
    true
);

-- Pending application awaiting admin review

INSERT INTO vendors (
    id, business_name, contact_name, email, phone, city, status
) VALUES (
    'v0000000-0000-4000-8000-000000000002',
    'ورشة النخيل',
    'خالد المطيري',
    'khalid.vendor@example.com',
    '+966551112233',
    'الرياض',
    'pending'
);

INSERT INTO vendor_bank_accounts (
    id, vendor_id, bank_name, account_holder, iban, is_primary, is_verified
) VALUES (
    'vb000000-0000-4000-8000-000000000002',
    'v0000000-0000-4000-8000-000000000002',
    'بنك الراجحي',
    'خالد المطيري',
    'SA442000000000001234567890',
    true,
    false
);
