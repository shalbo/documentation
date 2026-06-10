-- Registration profiles for customer, vendor, driver, workshop

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS city VARCHAR(60);

CREATE TABLE vendor_profiles (
    id                  UUID PRIMARY KEY,
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    shop_name           VARCHAR(120) NOT NULL,
    specialty           VARCHAR(120),
    city                VARCHAR(60) NOT NULL,
    latitude            NUMERIC(10, 7),
    longitude           NUMERIC(10, 7),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    is_approved         BOOLEAN NOT NULL DEFAULT false,
    rejection_reason    TEXT,
    vendor_id           UUID REFERENCES vendors(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vendor_profiles_approval ON vendor_profiles (is_approved, verification_status);

CREATE TABLE driver_profiles (
    id                  UUID PRIMARY KEY,
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    service_type        VARCHAR(20) NOT NULL
                        CHECK (service_type IN ('courier', 'tow')),
    plate_number        VARCHAR(20) NOT NULL,
    city                VARCHAR(60) NOT NULL,
    license_doc_path    VARCHAR(300),
    id_doc_path         VARCHAR(300),
    vehicle_doc_path    VARCHAR(300),
    is_approved         BOOLEAN NOT NULL DEFAULT false,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    rejection_reason    TEXT,
    technician_id       UUID REFERENCES technicians(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_driver_profiles_approval ON driver_profiles (is_approved, verification_status);

CREATE TABLE workshop_profiles (
    id                  UUID PRIMARY KEY,
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    center_name         VARCHAR(120) NOT NULL,
    specialty           VARCHAR(120),
    city                VARCHAR(60) NOT NULL,
    latitude            NUMERIC(10, 7),
    longitude           NUMERIC(10, 7),
    is_approved         BOOLEAN NOT NULL DEFAULT false,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    rejection_reason    TEXT,
    vendor_id           UUID REFERENCES vendors(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_workshop_profiles_approval ON workshop_profiles (is_approved, verification_status);
