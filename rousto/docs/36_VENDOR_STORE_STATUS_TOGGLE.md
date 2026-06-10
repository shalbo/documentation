# 36 — تفعيل وإيقاف المحل (Store Status Toggle)

يتيح للتاجر إخفاء بضاعته مؤقتاً من تطبيق الزبائن دون حذف المخزون.

---

## قاعدة البيانات

| الجدول | الحقل | الافتراضي |
|--------|-------|-----------|
| `vendors` | `is_active` | `true` |
| `vendor_profiles` | `is_active` | `true` (متزامن عند التبديل) |

---

## API

| الطريقة | المسار | الوصف |
|---------|--------|--------|
| PATCH | `/api/v1/vendor/status/toggle` | عكس حالة `is_active` للمحل الحالي |
| GET | `/api/v1/vendor/me` | يتضمن `is_active` |

المصادقة: `X-Vendor-Id` أو JWT

---

## فلترة الكتالوج

تُستبعد قطع الغيار التي لا تتوفر إلا لدى محلات `is_active = false` من:

- `GET /api/v1/parts/search`
- `GET /api/v1/parts/{id}`
- `GET /api/v1/marketplace/home`

---

## لوحة التاجر

- `vendor-products.html` و `vendor-portal.html` — زر تبديل في الهيدر
- `js/vendor-status-toggle.js` — تحديث الحالة فوراً بدون إعادة تحميل
