# 34 — تغذية مدن ليبيا (CitySeeder)

تغذية المدن والبلديات الرئيسية في جدول `cities` لتحديد نطاقات التوصيل، الشحن بين المدن، وفلترة المحلات والسائقين.

---

## هيكل الجدول

| العمود | الوصف |
|--------|--------|
| `id` | UUID ثابت لكل مدينة |
| `name_ar` | الاسم بالعربية |
| `name_en` | الاسم بالإنجليزية (فريد) |
| `region` | الإقليم: `West`، `East`، `South` |
| `is_active` | حالة التفعيل (افتراضي `true`) |

---

## الربط (Foreign Keys)

- `users.city_id`
- `vendors.city_id`
- `vendor_profiles.city_id`
- `driver_profiles.city_id`
- `workshop_profiles.city_id`
- `part_orders.origin_city_id` / `destination_city_id`
- `intercity_shipping_rates.origin_city_id` / `destination_city_id`

---

## إعادة التشغيل (مكافئ Laravel `CitySeeder`)

```bash
cd rousto/backend/api
python3 ../scripts/seed_libyan_cities.py
```

أو عبر SQL: `047_cities_schema.sql` + `047_libyan_cities_seed.sql` (مُضمّنان في `docker-compose.yml`).

---

## API

| الطريقة | المسار | الوصف |
|---------|--------|--------|
| GET | `/api/v1/cities` | قائمة المدن النشطة |
| GET | `/api/v1/cities?region=West` | فلترة حسب الإقليم |
| GET | `/api/v1/registration/cities` | نفس القائمة لنماذج التسجيل |

---

## البيانات

المصدر الوحيد: `app/city_seed_data.py` — **28 مدينة** (14 غرب، 8 شرق، 6 جنوب).
