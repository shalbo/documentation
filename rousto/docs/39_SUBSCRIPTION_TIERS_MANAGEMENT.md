# 39 — إدارة اشتراكات التجار والقيود البرمجية

## الجداول

| الجدول | الغرض |
|--------|--------|
| `tiers` | تعريف الباقات: `standard`, `professional`, `enterprise` |
| `subscriptions` | اشتراك التاجر، تاريخ البداية/الانتهاء، طريقة الدفع |
| `vendors.tier_id` | الباقة الحالية |
| `vendor_profiles.tier_id` | نسخة مرتبطة بالملف التجاري |

## القيود البرمجية (من قاعدة البيانات)

| القيد | التطبيق |
|-------|---------|
| `standard` — 100 قطعة كحد أقصى | `ensure_products_capacity` → رسالة: «لقد تجاوزت الحد المسموح به لبقاكتك الحالية، يرجى الترقية» |
| Excel/ZIP | `professional` و `enterprise` فقط — `require_excel_upload` |
| ترتيب البحث | `search_priority`: enterprise (300) > professional (200) > standard (100) |

## API

### التاجر
- `GET /api/v1/vendor/subscription`
- `POST /api/v1/vendor/subscription/upgrade-request`

### السوبر أدمن
- `GET /api/v1/admin/vendor-subscriptions`
- `PATCH /api/v1/admin/vendors/{id}/subscription`

## لوحات التحكم

| الشاشة | المسار |
|--------|--------|
| باقة الاشتراك (تاجر) | `admin/vendor-subscription.html` |
| إدارة اشتراكات التجار | `admin/vendor-subscriptions.html` |
| إعدادات الباقات | `admin/tiers.html` |
