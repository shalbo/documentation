-- Marketplace-first: fast geo lookup for vendors selling a given part

CREATE INDEX IF NOT EXISTS idx_part_inventory_part_vendor
    ON part_inventory (part_id, vendor_id)
    WHERE qty_available > 0;

CREATE INDEX IF NOT EXISTS idx_vendors_geo_approved
    ON vendors (base_lat, base_lng)
    WHERE status = 'approved' AND base_lat IS NOT NULL;
