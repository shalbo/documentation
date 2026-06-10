-- Driver registration activation fee (tow drivers)

ALTER TABLE driver_profiles
    ADD COLUMN IF NOT EXISTS registration_fee_status VARCHAR(10) NOT NULL DEFAULT 'unpaid'
        CHECK (registration_fee_status IN ('unpaid', 'paid', 'waived')),
    ADD COLUMN IF NOT EXISTS payment_reference_id UUID REFERENCES gateway_payments(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS registration_fee_gateway VARCHAR(20);

CREATE INDEX IF NOT EXISTS idx_driver_profiles_fee_status
    ON driver_profiles (registration_fee_status);
