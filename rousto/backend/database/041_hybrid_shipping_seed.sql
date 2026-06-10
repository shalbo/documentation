-- Intercity routes (Libya example: طرابلس ⇄ مصراتة)

INSERT INTO intercity_shipping_rates (
    id, origin_city, destination_city, flat_fee_sar, carrier_name, carrier_slug, eta_days
) VALUES
    ('is000000-0000-4000-8000-000000000001', 'طرابلس', 'مصراتة', 45.00,
     'ليبيا إكسبريس', 'libya-express', 2),
    ('is000000-0000-4000-8000-000000000002', 'مصراتة', 'طرابلس', 45.00,
     'ليبيا إكسبريس', 'libya-express', 2),
    ('is000000-0000-4000-8000-000000000003', 'الرياض', 'جدة', 55.00,
     'سمسا للشحن', 'smsa', 3),
    ('is000000-0000-4000-8000-000000000004', 'جدة', 'الرياض', 55.00,
     'سمسا للشحن', 'smsa', 3);
