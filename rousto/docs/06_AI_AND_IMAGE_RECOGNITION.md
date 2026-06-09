# 06 — الذكاء الاصطناعي والتعرف على الصور | AI & Image Recognition

فحص مبدئي بالصورة قبل الحجز — المستخدم يلتقط صورة لمشكلة السيارة ويحصل على تشخيص عربي وخدمات مقترحة.

- **المخطط:** [01_DATABASE_SCHEMA.md](01_DATABASE_SCHEMA.md)
- **الكتالوج:** [02_BACKEND_APIS.md](02_BACKEND_APIS.md)
- **المصادقة:** `X-User-Id` (مؤقت) — يُستبدل في `07_AUTH`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| رفع 1–3 صور لكل فحص | نماذج ML حقيقية / OpenAI Vision |
| محرك تشخيص تجريبي (قواعد + `scan_type`) | تدريب نماذج مخصصة |
| نتائج عربية + ربط بخدمات الكتالوج | OCR لوحة السيارة / VIN |
| سجل الفحوصات + ربط اختياري بالحجز | لوحة إدارة للفحوصات |
| شاشتا Flutter (التقاط + نتائج) | ML على الجهاز (TensorFlow Lite) |

---

## أنواع الفحص (scan_type)

| المعرّف | الوصف | الخدمة المقترحة |
|---------|-------|-----------------|
| `dashboard_warning` | أضواء تحذير على الطبلون | فحص كمبيوتر |
| `tire_tread` | إطار / تآكل | الإطارات والترصيص |
| `fluid_leak` | تسرب سوائل | تغيير الزيت |
| `body_damage` | خدش / صدمة | فحص كمبيوتر |
| `battery_corrosion` | بطارية / أكسدة | البطارية والكهرباء |

---

## جداول قاعدة البيانات

| الجدول | الغرض |
|--------|-------|
| `vehicle_scans` | جلسة فحص (مستخدم، مركبة، نوع، حالة) |
| `scan_images` | صور مرفوعة (`storage_key`) |
| `scan_findings` | نتائج التشخيص + `suggested_service_id` |
| `bookings.scan_id` | ربط الحجز بفحص سابق (اختياري) |

---

## API Endpoints

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/scans/types` | أنواع الفحص المتاحة | لا |
| POST | `/api/v1/scans` | رفع صور وبدء التحليل (multipart) | نعم |
| GET | `/api/v1/scans/{id}` | تفاصيل فحص + نتائج | نعم |
| GET | `/api/v1/me/scans` | سجل فحوصات المستخدم | نعم |
| GET | `/api/v1/scans/{id}/images/{image_id}` | تحميل صورة | نعم |

### مثال — `POST /api/v1/scans`

```http
POST /api/v1/scans
X-User-Id: a0000000-0000-4000-8000-000000000001
Content-Type: multipart/form-data

vehicle_id=b0000000-0000-4000-8000-000000000001
scan_type=dashboard_warning
images=@dashboard.jpg
```

```json
{
  "data": {
    "id": "s0000000-0000-4000-8000-000000000001",
    "vehicle_id": "b0000000-0000-4000-8000-000000000001",
    "scan_type": "dashboard_warning",
    "status": "completed",
    "findings": [
      {
        "code": "check_engine",
        "label_ar": "ضوء فحص المحرك",
        "severity": "medium",
        "confidence": 0.82,
        "suggested_service": {
          "slug": "diagnostics",
          "name_ar": "فحص كمبيوتر شامل"
        }
      }
    ],
    "images": [
      { "id": "...", "url": "/api/v1/scans/.../images/..." }
    ]
  }
}
```

### ربط الحجز

```json
POST /api/v1/bookings
{
  "service_id": "...",
  "vehicle_id": "...",
  "address_id": "...",
  "scan_id": "s0000000-0000-4000-8000-000000000001",
  "scheduled_at": "2026-06-10T10:00:00Z"
}
```

---

## محرك التشخيص (v1)

```
صورة/صور + scan_type
        ↓
  ai_diagnosis.py (قواعد ثابتة)
        ↓
  findings[] → services.slug
```

في الإنتاج: استبدال `analyze()` بموصل خارجي (OpenAI Vision، Google Cloud Vision) دون تغيير شكل الـ API.

متغيرات البيئة:

| المتغير | الافتراضي | الوصف |
|---------|-----------|-------|
| `SCAN_STORAGE_PATH` | `/data/scans` | مجلد حفظ الصور |
| `AI_PROVIDER` | `stub` | `stub` أو `external` (مستقبلاً) |

---

## واجهة التطبيق

| الشاشة | الملف | الوظيفة |
|--------|-------|---------|
| فحص بالصورة | `ai_scan_screen.dart` | اختيار نوع + التقاط صورة |
| نتائج الفحص | `scan_results_screen.dart` | عرض النتائج + «احجز الخدمة» |
| الرئيسية | `home_screen.dart` | بطاقة دخول «فحص بالصورة» |

---

## الملفات

```
rousto/backend/database/005_ai_schema.sql
rousto/backend/database/006_ai_seed.sql
rousto/backend/api/app/ai_diagnosis.py
rousto/backend/api/app/scan_services.py
rousto/backend/api/app/routers/scans.py
rousto/app_flutter/lib/screens/ai_scan_screen.dart
rousto/app_flutter/lib/screens/scan_results_screen.dart
```

---

## التشغيل

```bash
cd rousto/backend && docker compose down -v && docker compose up -d
curl http://localhost:8000/api/v1/scans/types
```

---

## الخطوة التالية

- `07_AUTH` — OTP + JWT
- `08_AI_EXTERNAL` — موصل رؤية حقيقي (اختياري)
