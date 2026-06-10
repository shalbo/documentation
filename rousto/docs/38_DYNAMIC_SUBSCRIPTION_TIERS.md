# 38 — إدارة باقات المنصة الديناميكية (Dynamic Subscription Tiers)

مكافئ Laravel `tiers` + Middleware يقرأ `$vendor->tier` — مُنفَّذ في FastAPI + PostgreSQL + لوحة السوبر أدمن.

---

## قاعدة البيانات

### جدول `tiers`

| العمود | النوع | الوصف |
|--------|-------|--------|
| `id` | UUID | المعرّف |
| `name_ar` / `name_en` | VARCHAR | اسم الباقة |
| `price` | NUMERIC | السعر |
| `products_limit` | INTEGER | سقف القطع (**`-1` = غير محدود**) |
| `allow_excel_upload` | BOOLEAN | رفع Excel جماعي |
| `allow_vin_decoder` | BOOLEAN | ربط VIN / فك ترميز |
| `allow_unlimited_chat` | BOOLEAN | محادثة غير محدودة |
| `has_gold_badge` | BOOLEAN | شارة ذهبية في السوق |

### ربط التاجر

- `vendors.tier_id` → `tiers.id`
- التاجر الجديد يُعيَّن تلقائياً لباقة `starter`

**Migrations:** `052_vendor_tiers.sql`, `052_vendor_tiers_seed.sql`

---

## API الإدارة

| الطريقة | المسار |
|---------|--------|
| GET | `/api/v1/admin/tiers` |
| GET | `/api/v1/admin/tiers/{id}` |
| PUT | `/api/v1/admin/tiers/{id}` |

مثال تحديث:

```json
PUT /api/v1/admin/tiers/{id}
{
  "price": 299,
  "products_limit": -1,
  "allow_excel_upload": true,
  "allow_vin_decoder": true,
  "has_gold_badge": true
}
```

---

## تطبيق القيود (من قاعدة البيانات)

| الميزة | نقطة التطبيق |
|--------|--------------|
| `products_limit` | `vendor_create_product`, `process_bulk_upload` |
| `allow_excel_upload` | قالب Excel + `bulk-upload` |
| `allow_vin_decoder` | إنشاء قطعة بـ `vin_prefixes` + استيراد Excel |
| `has_gold_badge` | `marketplace_services._vendor_out` → `has_gold_badge` |
| `allow_unlimited_chat` | `tier_services.require_unlimited_chat()` جاهز للربط |

---

## لوحة السوبر أدمن

- `rousto/admin/tiers.html` — بطاقات باقات مع Toggle Switches
- `rousto/admin/js/tiers-admin.js` — حفظ فوري عبر PUT

---

## API التاجر

```
GET /api/v1/vendor/parts/tier
```

يعرض الباقة الحالية واستخدام المخزون (`products_count` / `products_remaining`).
