"""Comprehensive spare-parts category tree (main + sub) — Libyan catalog."""

from __future__ import annotations

# slug -> (name_ar, name_en, icon_key)
MAIN_CATEGORIES: dict[str, tuple[str, str, str]] = {
    "engine": ("المحرك وملحقاته", "Engine & Accessories", "engine"),
    "suspension": ("منظومة الحركة والفرامل", "Drivetrain & Brakes", "suspension"),
    "electrical": ("الكهرباء والإلكترونيات", "Electrical & Electronics", "electrical"),
    "fuel": ("منظومة الوقود والعادم", "Fuel & Exhaust", "fuel"),
    "ac": ("التكييف والتبريد", "AC & Cooling", "ac"),
    "fluids": ("الفلاتر والزيوت والمواد الاستهلاكية", "Filters, Oils & Consumables", "fluids"),
    "body": ("الهيكل الخارجي والزجاج", "Body & Glass", "body"),
    "interior": ("الأكسسوارات والقطع الداخلية", "Interior & Accessories", "interior"),
}

# (slug, name_ar, name_en, parent_slug, icon_key)
SUB_CATEGORIES: list[tuple[str, str, str, str, str]] = [
    # المحرك
    ("engine-internal", "أجزاء المحرك الداخلية", "Internal Engine Parts", "engine", "piston"),
    ("engine-cooling", "نظام التبريد (Cooling)", "Cooling System", "engine", "cooling"),
    ("belts-timing", "السيور والكاتينات", "Belts & Timing", "engine", "belt"),
    ("engine-mounts", "قواعد المحرك والكمبيو", "Engine Mounts & ECU", "engine", "engine_mount"),
    # الحركة والفرامل
    ("brakes", "منظومة الفرامل (Brakes)", "Brake System", "suspension", "brake_pad"),
    ("suspension-parts", "منظومة التعليق (Suspension)", "Suspension System", "suspension", "shock"),
    ("steering", "منظومة التوجيه (Steering)", "Steering System", "suspension", "steering"),
    ("wheels-drivetrain", "العجلات ونقل الحركة", "Wheels & Drivetrain", "suspension", "wheel"),
    # الكهرباء
    ("ignition", "منظومة التشغيل والاحتراق", "Ignition System", "electrical", "spark_plug"),
    ("sensors-ecu", "الحساسات والكمبيوترات", "Sensors & ECU", "electrical", "sensor"),
    ("lighting", "الإنارة والمصابيح", "Lighting", "electrical", "headlight"),
    # الوقود
    ("fuel-system", "منظومة الوقود وضخ البنزين", "Fuel System & Pumps", "fuel", "fuel_pump"),
    ("exhaust", "منظومة الهواء والعادم (الشكمان)", "Air & Exhaust", "fuel", "exhaust"),
    # التكييف
    ("ac-compressor", "كمبروسرات وراديترات المكيف", "AC Compressors & Radiators", "ac", "ac_compressor"),
    ("ac-filters", "فلاتر وثلاجات التكييف", "AC Filters & Evaporators", "ac", "ac_filter"),
    # الزيوت والفلاتر
    ("maintenance-filters", "فلاتر الصيانة الدورية", "Maintenance Filters", "fluids", "oil_filter"),
    ("oils-fluids", "الزيوت والسوائل التشغيلية", "Oils & Operating Fluids", "fluids", "oil_barrel"),
    # الهيكل
    ("body-panels", "قطع الهيكل والبرواكني", "Body Panels & Bumpers", "body", "bumper"),
    ("glass-mirrors", "الزجاج والمرايا الجانبية", "Glass & Side Mirrors", "body", "mirror"),
    # قطع داخلية
    ("accessories", "كماليات وأكسسوارات السيارة", "Car Accessories", "interior", "accessory"),
    ("interior-salon", "قطع الصالون الداخلي وأحزمة الأمان", "Interior & Seat Belts", "interior", "seat_belt"),
]

# Stable UUIDs for SQL/docker init (slug -> id)
MAIN_CATEGORY_IDS: dict[str, str] = {
    "engine": "c1000000-0000-4000-8000-000000000001",
    "suspension": "c1000000-0000-4000-8000-000000000002",
    "electrical": "c1000000-0000-4000-8000-000000000003",
    "fuel": "c1000000-0000-4000-8000-000000000004",
    "ac": "c1000000-0000-4000-8000-000000000005",
    "fluids": "c1000000-0000-4000-8000-000000000006",
    "body": "c1000000-0000-4000-8000-000000000007",
    "interior": "c1000000-0000-4000-8000-000000000008",
}

SUB_CATEGORY_IDS: dict[str, str] = {
    "engine-internal": "c1000000-0000-4000-8000-000000000101",
    "engine-cooling": "c1000000-0000-4000-8000-000000000102",
    "belts-timing": "c1000000-0000-4000-8000-000000000103",
    "engine-mounts": "c1000000-0000-4000-8000-000000000104",
    "brakes": "c1000000-0000-4000-8000-000000000105",
    "suspension-parts": "c1000000-0000-4000-8000-000000000106",
    "steering": "c1000000-0000-4000-8000-000000000107",
    "wheels-drivetrain": "c1000000-0000-4000-8000-000000000108",
    "ignition": "c1000000-0000-4000-8000-000000000109",
    "sensors-ecu": "c1000000-0000-4000-8000-000000000110",
    "lighting": "c1000000-0000-4000-8000-000000000111",
    "fuel-system": "c1000000-0000-4000-8000-000000000112",
    "exhaust": "c1000000-0000-4000-8000-000000000113",
    "ac-compressor": "c1000000-0000-4000-8000-000000000114",
    "ac-filters": "c1000000-0000-4000-8000-000000000115",
    "maintenance-filters": "c1000000-0000-4000-8000-000000000116",
    "oils-fluids": "c1000000-0000-4000-8000-000000000117",
    "body-panels": "c1000000-0000-4000-8000-000000000118",
    "glass-mirrors": "c1000000-0000-4000-8000-000000000119",
    "accessories": "c1000000-0000-4000-8000-000000000120",
    "interior-salon": "c1000000-0000-4000-8000-000000000121",
}
