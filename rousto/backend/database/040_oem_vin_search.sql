-- Advanced OEM / VIN prefix search indexes

ALTER TABLE parts
    ADD COLUMN IF NOT EXISTS oem_number VARCHAR(60),
    ADD COLUMN IF NOT EXISTS vin_prefix VARCHAR(11);

UPDATE parts SET oem_number = part_number WHERE oem_number IS NULL;

CREATE INDEX IF NOT EXISTS idx_parts_oem_number ON parts (oem_number) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_parts_vin_prefix ON parts (vin_prefix) WHERE vin_prefix IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_parts_oem_vin_combo ON parts (oem_number, vin_prefix);

-- Seed VIN prefixes for Toyota Camry / Corolla examples
UPDATE parts SET vin_prefix = '4T1B11HK5' WHERE slug = 'toyota-oil-filter-camry';
UPDATE parts SET vin_prefix = '4T1B11HK5' WHERE slug = 'toyota-air-filter';
UPDATE parts SET oem_number = 'TOY-04152-YZZA1' WHERE slug = 'toyota-oil-filter-camry';
UPDATE parts SET oem_number = 'TOY-90915-YZZD2' WHERE slug = 'toyota-air-filter';
