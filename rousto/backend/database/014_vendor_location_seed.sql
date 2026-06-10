-- Base location for approved seed vendor (أحمد الفني — near active booking)

UPDATE vendors
SET
    base_lat = 24.7700000,
    base_lng = 46.7350000,
    service_radius_km = 20.00
WHERE id = 'v0000000-0000-4000-8000-000000000001';
