-- Guaranteed Fitment Selector — structured vehicle catalog

CREATE TABLE car_makes (
    id          UUID PRIMARY KEY,
    slug        VARCHAR(40) NOT NULL UNIQUE,
    name_ar     VARCHAR(80) NOT NULL,
    name_en     VARCHAR(80),
    is_active   BOOLEAN NOT NULL DEFAULT true,
    sort_order  SMALLINT NOT NULL DEFAULT 0
);

CREATE TABLE car_models (
    id          UUID PRIMARY KEY,
    make_id     UUID NOT NULL REFERENCES car_makes(id) ON DELETE CASCADE,
    slug        VARCHAR(40) NOT NULL,
    name_ar     VARCHAR(80) NOT NULL,
    name_en     VARCHAR(80),
    is_active   BOOLEAN NOT NULL DEFAULT true,
    UNIQUE (make_id, slug)
);

CREATE TABLE car_years (
    id          UUID PRIMARY KEY,
    model_id    UUID NOT NULL REFERENCES car_models(id) ON DELETE CASCADE,
    year        SMALLINT NOT NULL CHECK (year >= 1980 AND year <= 2035),
    is_active   BOOLEAN NOT NULL DEFAULT true,
    UNIQUE (model_id, year)
);

CREATE INDEX idx_car_models_make ON car_models (make_id, is_active);
CREATE INDEX idx_car_years_model ON car_years (model_id, year);

CREATE TABLE part_vehicle_compatibilities (
    id          UUID PRIMARY KEY,
    part_id     UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    car_year_id UUID NOT NULL REFERENCES car_years(id) ON DELETE CASCADE,
    fitment_note_ar VARCHAR(200),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (part_id, car_year_id)
);

CREATE INDEX idx_part_fitment_year ON part_vehicle_compatibilities (car_year_id);
CREATE INDEX idx_part_fitment_part ON part_vehicle_compatibilities (part_id);
