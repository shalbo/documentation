-- Tier commission rates + platform system wallet

UPDATE tiers SET platform_commission_rate = 0.1500 WHERE slug = 'standard';
UPDATE tiers SET platform_commission_rate = 0.1200 WHERE slug = 'professional';
UPDATE tiers SET platform_commission_rate = 0.0800 WHERE slug = 'enterprise';

INSERT INTO wallets (id, owner_type, owner_id, balance_lyd, currency)
VALUES (
    'w1000000-0000-4000-8000-000000000099',
    'platform',
    '00000000-0000-4000-8000-000000000099',
    0,
    'LYD'
)
ON CONFLICT (owner_type, owner_id) DO NOTHING;
