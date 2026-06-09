# 01 — مخطط قاعدة البيانات | Database Schema

منصة **روستو** (Rousto) — عناية ذكية بالسيارات عند موقع العميل.

- **قاعدة البيانات:** PostgreSQL 16+
- **الترميز:** UTF-8 (دعم العربية)
- **المعرّفات:** UUID v4
- **المنطقة الزمنية:** `Asia/Riyadh`

---

## مخطط العلاقات (ER)

```mermaid
erDiagram
    users ||--o{ vehicles : owns
    users ||--o{ addresses : has
    users ||--o{ payment_methods : has
    users ||--o{ bookings : places
    users ||--o{ loyalty_transactions : earns

    service_categories ||--o{ services : contains
    services ||--o{ bookings : booked_as

    vehicles ||--o{ bookings : for_vehicle
    addresses ||--o{ bookings : at_address
    payment_methods ||--o{ bookings : paid_with
    technicians ||--o{ bookings : assigned_to

    bookings ||--o{ booking_status_events : tracks
    bookings ||--o{ payments : has
    bookings }o--o| promotions : uses

    promotions ||--o{ promotion_redemptions : redeemed
```

---

## الجداول

### 1. `users` — المستخدمون

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | المعرّف |
| `full_name` | VARCHAR(120) | الاسم الكامل |
| `email` | VARCHAR(255) UNIQUE | البريد |
| `phone` | VARCHAR(20) UNIQUE | الجوال (+966…) |
| `avatar_initials` | CHAR(1) | حرف الأفاتار |
| `loyalty_points` | INTEGER DEFAULT 0 | رصيد النقاط |
| `locale` | VARCHAR(5) DEFAULT 'ar' | اللغة |
| `is_active` | BOOLEAN DEFAULT true | نشط |
| `created_at` | TIMESTAMPTZ | تاريخ التسجيل |
| `updated_at` | TIMESTAMPTZ | آخر تحديث |

### 2. `vehicles` — المركبات

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK → users | المالك |
| `make` | VARCHAR(60) | الشركة (تويوتا) |
| `model` | VARCHAR(60) | الموديل (كامري) |
| `year` | SMALLINT | سنة الصنع |
| `color` | VARCHAR(40) | اللون |
| `plate_number` | VARCHAR(20) | رقم اللوحة |
| `is_default` | BOOLEAN | المركبة الافتراضية |
| `created_at` | TIMESTAMPTZ | |

### 3. `service_categories` — تصنيفات الخدمات

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `slug` | VARCHAR(40) UNIQUE | معرّف إنجليزي (oil, tires…) |
| `name_ar` | VARCHAR(80) | الاسم بالعربية |
| `sort_order` | SMALLINT | ترتيب العرض |
| `is_active` | BOOLEAN | |

### 4. `services` — الخدمات

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `category_id` | UUID FK | التصنيف |
| `slug` | VARCHAR(60) UNIQUE | |
| `name_ar` | VARCHAR(120) | اسم الخدمة |
| `subtitle_ar` | VARCHAR(200) | وصف مختصر |
| `icon_key` | VARCHAR(40) | مفتاح الأيقونة (oil_barrel…) |
| `price_sar` | NUMERIC(10,2) | السعر بالدينار |
| `duration_minutes` | SMALLINT | المدة بالدقائق |
| `is_active` | BOOLEAN | |
| `created_at` | TIMESTAMPTZ | |

### 5. `addresses` — العناوين

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK | |
| `label` | VARCHAR(40) | التسمية (المنزل، العمل) |
| `district` | VARCHAR(80) | الحي |
| `city` | VARCHAR(60) | المدينة |
| `latitude` | NUMERIC(10,7) | |
| `longitude` | NUMERIC(10,7) | |
| `is_default` | BOOLEAN | |
| `created_at` | TIMESTAMPTZ | |

### 6. `payment_methods` — طرق الدفع

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK | |
| `type` | ENUM | mada, apple_pay, visa, mastercard |
| `last_four` | CHAR(4) | آخر 4 أرقام |
| `label_ar` | VARCHAR(60) | التسمية (مدى **** 4421) |
| `is_default` | BOOLEAN | |
| `created_at` | TIMESTAMPTZ | |

### 7. `technicians` — الفنيون

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `full_name` | VARCHAR(120) | |
| `phone` | VARCHAR(20) | |
| `rating` | NUMERIC(2,1) | التقييم (4.9) |
| `avatar_initials` | CHAR(1) | |
| `is_available` | BOOLEAN | متاح للتعيين |
| `current_lat` | NUMERIC(10,7) | الموقع الحالي |
| `current_lng` | NUMERIC(10,7) | |
| `created_at` | TIMESTAMPTZ | |

### 8. `promotions` — العروض والخصومات

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `code` | VARCHAR(30) UNIQUE | كود الخصم (ROUSTO) |
| `title_ar` | VARCHAR(120) | عنوان العرض |
| `description_ar` | VARCHAR(300) | |
| `discount_type` | ENUM | percentage, fixed_amount |
| `discount_value` | NUMERIC(10,2) | قيمة الخصم |
| `min_order_sar` | NUMERIC(10,2) | الحد الأدنى |
| `max_uses_per_user` | SMALLINT | |
| `starts_at` | TIMESTAMPTZ | |
| `ends_at` | TIMESTAMPTZ | |
| `is_active` | BOOLEAN | |

### 9. `bookings` — الحجوزات / الطلبات

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `reference` | VARCHAR(12) UNIQUE | رقم مرجعي (RST-2026-001) |
| `user_id` | UUID FK | العميل |
| `service_id` | UUID FK | الخدمة |
| `vehicle_id` | UUID FK | المركبة |
| `address_id` | UUID FK | موقع الخدمة |
| `payment_method_id` | UUID FK | طريقة الدفع |
| `technician_id` | UUID FK NULL | الفني المعيّن |
| `promotion_id` | UUID FK NULL | العرض المطبّق |
| `scheduled_at` | TIMESTAMPTZ | موعد الخدمة |
| `service_price_sar` | NUMERIC(10,2) | سعر الخدمة |
| `discount_sar` | NUMERIC(10,2) | الخصم |
| `total_sar` | NUMERIC(10,2) | الإجمالي |
| `status` | ENUM | انظر أدناه |
| `notes` | TEXT | ملاحظات |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

**حالات الحجز (`booking_status`):**

| القيمة | الوصف |
|--------|-------|
| `pending` | بانتظار التأكيد |
| `confirmed` | تم تأكيد الحجز |
| `technician_assigned` | تم تعيين الفني |
| `en_route` | الفني في الطريق |
| `in_progress` | تنفيذ الخدمة |
| `completed` | اكتمال الخدمة |
| `cancelled` | ملغى |

### 10. `booking_status_events` — سجل تتبّع الحجز

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `booking_id` | UUID FK | |
| `status` | booking_status | الحالة |
| `label_ar` | VARCHAR(120) | النص المعروض |
| `occurred_at` | TIMESTAMPTZ | وقت الحدث |
| `metadata` | JSONB | بيانات إضافية (ETA…) |

### 11. `payments` — المدفوعات

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `booking_id` | UUID FK | |
| `amount_sar` | NUMERIC(10,2) | المبلغ |
| `status` | ENUM | pending, captured, refunded, failed |
| `gateway_ref` | VARCHAR(100) | مرجع بوابة الدفع |
| `paid_at` | TIMESTAMPTZ | |
| `created_at` | TIMESTAMPTZ | |

### 12. `loyalty_transactions` — حركات النقاط

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK | |
| `booking_id` | UUID FK NULL | |
| `points` | INTEGER | موجب = كسب، سالب = استبدال |
| `reason_ar` | VARCHAR(200) | السبب |
| `created_at` | TIMESTAMPTZ | |

### 13. `testimonials` — آراء العملاء

| العمود | النوع | الوصف |
|--------|-------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK NULL | |
| `author_name` | VARCHAR(80) | |
| `city` | VARCHAR(60) | |
| `quote_ar` | TEXT | |
| `rating` | SMALLINT | 1–5 |
| `is_published` | BOOLEAN | |
| `created_at` | TIMESTAMPTZ | |

---

## الفهارس (Indexes)

| الجدول | الفهرس | الغرض |
|--------|--------|-------|
| bookings | `(user_id, created_at DESC)` | سجل الطلبات |
| bookings | `(status)` | لوحة التحكم |
| bookings | `(technician_id, status)` | مهام الفني |
| booking_status_events | `(booking_id, occurred_at)` | التتبّع |
| services | `(category_id, is_active)` | قائمة الخدمات |
| vehicles | `(user_id)` | سيارات المستخدم |

---

## الملفات التنفيذية

```
rousto/backend/database/
├── 001_schema.sql    # إنشاء الجداول والأنواع والفهارس
├── 002_seed.sql      # بيانات تجريبية (مطابقة للتطبيق)
└── README.md         # تعليمات التشغيل
```

### التشغيل السريع

```bash
cd rousto/backend
docker compose up -d
docker compose exec db psql -U rousto -d rousto -f /docker-entrypoint-initdb.d/001_schema.sql
docker compose exec db psql -U rousto -d rousto -f /docker-entrypoint-initdb.d/002_seed.sql
```

---

## الخطوة التالية

- [`02_BACKEND_APIS`](02_BACKEND_APIS.md) — واجهات REST للتطبيق والويب ✅
- `03_AUTH` — المصادقة (OTP / JWT)
