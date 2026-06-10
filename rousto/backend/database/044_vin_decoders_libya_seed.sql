-- Comprehensive Libyan market VIN decoder (Toyota, Hyundai, Kia, US/Korean imports, Europe)

INSERT INTO vin_decoders (id, vin_prefix, make, model, year_range, engine, market) VALUES
    -- Toyota
    ('vd000000-0000-4000-8000-000000000001', 'JTMCE90E', 'Toyota', 'Corolla', '2015-2019', '1.6L VVTi', 'libya'),
    ('vd000000-0000-4000-8000-000000000002', 'JTNBF1FK', 'Toyota', 'Camry', '2018-2022', '2.5L D4S', 'libya'),
    ('vd000000-0000-4000-8000-000000000003', 'JTDKN3DU', 'Toyota', 'Prius', '2016-2021', '1.8L Hybrid', 'libya'),
    ('vd000000-0000-4000-8000-000000000004', '4T1BK1EB', 'Toyota', 'Avalon', '2013-2018', '3.5L V6 (US Spec)', 'libya'),
    ('vd000000-0000-4000-8000-000000000005', 'JTMDFRFV', 'Toyota', 'Rav4', '2016-2021', '2.5L Dual VVTi', 'libya'),
    -- Hyundai
    ('vd000000-0000-4000-8000-000000000006', 'KMHCT41M', 'Hyundai', 'Elantra', '2016-2020', '1.6L / 2.0L MPI', 'libya'),
    ('vd000000-0000-4000-8000-000000000007', 'KMHDU41R', 'Hyundai', 'Avante / Elantra', '2012-2016', '1.6L GDI (KDM)', 'libya'),
    ('vd000000-0000-4000-8000-000000000008', 'KMHJU81B', 'Hyundai', 'Tucson', '2017-2021', '2.0L GDI', 'libya'),
    ('vd000000-0000-4000-8000-000000000009', 'KMHCT41C', 'Hyundai', 'Accent', '2014-2019', '1.4L / 1.6L MPI', 'libya'),
    ('vd000000-0000-4000-8000-00000000000a', 'KMHJU81D', 'Hyundai', 'Santa Fe', '2013-2018', '2.4L / 3.3L V6', 'libya'),
    ('vd000000-0000-4000-8000-00000000000b', 'KMHSH41D', 'Hyundai', 'Azera', '2015-2019', '3.0L / 3.3L V6', 'libya'),
    -- Kia
    ('vd000000-0000-4000-8000-00000000000c', 'KNAFX412', 'Kia', 'Cerato', '2016-2021', '1.6L MPI', 'libya'),
    ('vd000000-0000-4000-8000-00000000000d', 'KNAJU52A', 'Kia', 'Sportage', '2017-2022', '2.0L Nu MPI', 'libya'),
    ('vd000000-0000-4000-8000-00000000000e', 'KNAGT41M', 'Kia', 'Optima / K5', '2014-2019', '2.0L LPI (Gas) / 2.4L', 'libya'),
    ('vd000000-0000-4000-8000-00000000000f', 'KNABX413', 'Kia', 'Rio', '2012-2017', '1.4L MPI', 'libya'),
    -- Chevrolet & Renault Samsung (Korean imports)
    ('vd000000-0000-4000-8000-000000000010', 'KL1TA69Z', 'Chevrolet', 'Cruze / Lacetti', '2010-2016', '1.6L / 1.4L Turbo', 'libya'),
    ('vd000000-0000-4000-8000-000000000011', 'KNMAT103', 'Renault Samsung', 'SM3 / SM5', '2011-2017', '1.6L / 2.0L Nissan Eng.', 'libya'),
    -- European (common in Tripoli & Misrata)
    ('vd000000-0000-4000-8000-000000000012', 'WDDGF8AB', 'Mercedes-Benz', 'C-Class', '2012-2018', '1.6L / 2.0L Turbo', 'libya'),
    ('vd000000-0000-4000-8000-000000000013', 'WBA3B1C5', 'BMW', '3 Series', '2012-2018', '2.0L TwinPower', 'libya'),
    ('vd000000-0000-4000-8000-000000000014', 'WVWZZZ3C', 'Volkswagen', 'Passat', '2011-2018', '1.4L TSI / 2.0L TDI', 'libya'),
    ('vd000000-0000-4000-8000-000000000015', 'VF3LCYHR', 'Peugeot', '301 / 308', '2013-2019', '1.6L VTi / HDi', 'libya'),
    ('vd000000-0000-4000-8000-000000000016', 'VF1RFA00', 'Renault', 'Symbol / Fluence', '2012-2018', '1.6L 16V', 'libya'),
    -- American (US-spec imports)
    ('vd000000-0000-4000-8000-000000000017', '1G1BC5SM', 'Chevrolet', 'Malibu', '2013-2018', '2.4L / 2.5L (US)', 'libya'),
    ('vd000000-0000-4000-8000-000000000018', '1FAHP2D8', 'Ford', 'Fusion', '2013-2018', '2.5L / EcoBoost', 'libya')
ON CONFLICT (vin_prefix) DO UPDATE SET
    make = EXCLUDED.make,
    model = EXCLUDED.model,
    year_range = EXCLUDED.year_range,
    engine = EXCLUDED.engine,
    market = EXCLUDED.market,
    updated_at = NOW();
