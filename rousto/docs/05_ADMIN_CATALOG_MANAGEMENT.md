# 05 — إدارة الكتالوج (لوحة الإدارة) | Admin Catalog Management

لوحة إدارة **تصنيفات الخدمات** و**الخدمات** لمنصة روستو — بدون تعديل SQL يدوياً.

- **الكتالوج العام:** [02_BACKEND_APIS.md](02_BACKEND_APIS.md) (قراءة فقط)
- **المخطط:** [01_DATABASE_SCHEMA.md](01_DATABASE_SCHEMA.md) — جداول `service_categories` و `services`
- **المصادقة (مؤقتة):** هيدر `X-Admin-Key` — يُستبدل بـ JWT + دور `admin` في `07_AUTH`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| CRUD تصنيفات (إنشاء، تعديل، ترتيب، إخفاء) | رفع صور / أيقونات |
| CRUD خدمات (سعر، مدة، تصنيف، إخفاء) | إدارة العروض والاشتراكات |
| لوحة ويب RTL عربية | تطبيق جوال للإدارة |
| اختبارات API | حذف نهائي (يُستخدم `is_active`) |

---

## المصادقة (مؤقتة)

```
X-Admin-Key: rousto_admin_dev
```

المفتاح الافتراضي في بيئة التطوير. غيّره عبر متغير البيئة `ADMIN_API_KEY`.

| HTTP | المعنى |
|------|--------|
| 401 | مفتاح مفقود أو خاطئ |
| 403 | محاولة تعديل تصنيف `all` المحمي |
| 404 | السجل غير موجود |
| 409 | `slug` مكرر |

---

## API Endpoints

### التصنيفات

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/categories` | كل التصنيفات (نشطة وغير نشطة) |
| POST | `/api/v1/admin/categories` | إنشاء تصنيف |
| GET | `/api/v1/admin/categories/{id}` | تفاصيل تصنيف |
| PATCH | `/api/v1/admin/categories/{id}` | تعديل (`name_ar`, `sort_order`, `is_active`) |
| POST | `/api/v1/admin/categories/reorder` | إعادة ترتيب دفعة واحدة |

### الخدمات

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/services` | كل الخدمات (`?category=oil`, `?active=true`) |
| POST | `/api/v1/admin/services` | إنشاء خدمة |
| GET | `/api/v1/admin/services/{id}` | تفاصيل خدمة |
| PATCH | `/api/v1/admin/services/{id}` | تعديل الحقول |

---

## قواعد العمل

1. **`slug = all`** — تصنيف افتراضي يعرض كل الخدمات في شجرة التطبيق؛ لا يُحذف ولا يُعطّل.
2. **إخفاء بدل الحذف** — `is_active = false`؛ الخدمات المخفية لا تظهر في `/categories/tree` ولا `/services`.
3. **ربط الخدمة** — `category_id` يجب أن يشير لتصنيف حقيقي (ليس `all`).
4. **`slug`** — أحرف إنجليزية صغيرة وأرقام وشرطات فقط؛ فريد على مستوى الجدول.
5. **السعر** — بالدينار (`price_sar` داخلياً).

---

## أمثلة

### إنشاء خدمة

```http
POST /api/v1/admin/services
X-Admin-Key: rousto_admin_dev
Content-Type: application/json

{
  "category_id": "e0000000-0000-4000-8000-000000000002",
  "slug": "oil-premium",
  "name_ar": "زيت بريميوم",
  "subtitle_ar": "زيت اصطناعي كامل",
  "icon_key": "oil_barrel",
  "price_sar": 180,
  "duration_minutes": 50
}
```

```json
{
  "data": {
    "id": "...",
    "slug": "oil-premium",
    "name_ar": "زيت بريميوم",
    "price_sar": 180.0,
    "duration_minutes": 50,
    "category_slug": "oil",
    "is_active": true
  }
}
```

### إعادة ترتيب التصنيفات

```http
POST /api/v1/admin/categories/reorder
X-Admin-Key: rousto_admin_dev

{
  "items": [
    { "id": "e0000000-0000-4000-8000-000000000002", "sort_order": 1 },
    { "id": "e0000000-0000-4000-8000-000000000003", "sort_order": 2 }
  ]
}
```

---

## لوحة الويب

```
rousto/admin/
├── index.html      # واجهة إدارة الكتالوج
├── css/admin.css
└── js/admin.js     # اتصال بالـ API
```

### التشغيل

```bash
cd rousto/backend && docker compose up -d
cd rousto && python3 -m http.server 8080
# افتح http://localhost:8080/admin/index.html
```

أدخل مفتاح الإدارة (`rousto_admin_dev`) وعنوان API (`http://localhost:8000`).

---

## الملفات

```
rousto/docs/05_ADMIN_CATALOG_MANAGEMENT.md
rousto/backend/api/app/deps.py              # require_admin_key
rousto/backend/api/app/routers/admin_catalog.py
rousto/backend/api/app/schemas.py           # نماذج Admin*
rousto/backend/api/tests/test_admin_catalog.py
rousto/admin/index.html
rousto/admin/css/admin.css
rousto/admin/js/admin.js
```

---

## التأثير على الواجهات العامة

| Endpoint عام | السلوك بعد التعديل |
|--------------|-------------------|
| `GET /categories/tree` | يقرأ `is_active` فقط — التغييرات فورية |
| `GET /services` | يستبعد الخدمات المخفية |
| `POST /bookings` | يرفض `service_id` لخدمة مخفية |

---

## الخطوة التالية

- `07_AUTH` — OTP + JWT + أدوار (`admin`, `customer`, `technician`)
- `08_ADMIN_PROMOTIONS` — إدارة أكواد الخصم والعروض
