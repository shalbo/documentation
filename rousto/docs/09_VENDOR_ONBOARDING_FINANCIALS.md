# 09 — انضمام الفنيين والمالية | Vendor Onboarding & Financials

تسجيل **فنيي الخدمة** (مقدّمي الخدمة)، مراجعة طلبات الانضمام من الإدارة، وربط **الحسابات البنكية** بحصص الدفع من محرك التقسيم.

- **تقسيم المدفوعات:** [08_SPLIT_PAYMENTS_ENGINE.md](08_SPLIT_PAYMENTS_ENGINE.md)
- **المخطط:** `vendors`, `vendor_bank_accounts`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| تقديم طلب انضمام (نموذج عام) | KYC / تحقق هوية حكومي |
| مراجعة وموافقة/رفض من الإدارة | تحويل بنكي فعلي |
| ربط الفني بجدول `technicians` عند الموافقة | بوابات دفع |
| إدارة IBAN وحساب بنكي أساسي | فواتير ضريبية |
| عرض حصص الدفع (`payment_split_legs`) | تطبيق جوال للفني |

---

## حالات الطلب

| الحالة | الوصف |
|--------|-------|
| `draft` | مسودة (غير مستخدمة في MVP) |
| `pending` | بانتظار مراجعة الإدارة |
| `approved` | مُوافَق عليه — مرتبط بـ `technician_id` |
| `rejected` | مرفوض مع `rejection_reason` |
| `suspended` | موقوف مؤقتاً |

---

## جداول قاعدة البيانات

| الجدول | الغرض |
|--------|-------|
| `vendors` | طلبات انضمام الفنيين + حالة المراجعة |
| `vendor_bank_accounts` | حساب بنكي أساسي (IBAN) لكل فني مُوافَق |

---

## المصادقة (مؤقتة)

| الدور | الهيدر |
|-------|--------|
| إدارة | `X-Admin-Key: rousto_admin_dev` |
| فني (بعد الموافقة) | `X-Vendor-Id: <vendor_uuid>` |

يُستبدل بـ JWT + أدوار في `11_AUTH`.

---

## API Endpoints

### عام

| Method | Path | الوصف |
|--------|------|-------|
| POST | `/api/v1/vendors/applications` | تقديم طلب انضمام |

### بوابة الفني

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/vendor/me` | الملف + الحساب البنكي + ملخص المدفوعات | Vendor |
| PUT | `/api/v1/vendor/me/financials` | تحديث IBAN والبنك | Vendor (approved) |
| GET | `/api/v1/vendor/me/payouts` | قائمة حصص الدفع | Vendor (approved) |

### إدارة

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/vendors` | كل الطلبات (`?status=pending`) |
| GET | `/api/v1/admin/vendors/{id}` | تفاصيل طلب |
| POST | `/api/v1/admin/vendors/{id}/approve` | الموافقة + ربط/إنشاء فني |
| POST | `/api/v1/admin/vendors/{id}/reject` | الرفض مع سبب |

---

## أمثلة

### تقديم طلب

```http
POST /api/v1/vendors/applications
Content-Type: application/json

{
  "business_name": "ورشة النخيل",
  "contact_name": "خالد المطيري",
  "email": "khalid@example.com",
  "phone": "+966551112233",
  "city": "الرياض",
  "bank_name": "البنك الأهلي",
  "account_holder": "خالد المطيري",
  "iban": "SA0380000000608010167519"
}
```

### ملف الفني — `GET /api/v1/vendor/me`

```json
{
  "data": {
    "id": "v0000000-0000-4000-8000-000000000001",
    "business_name": "خدمات أحمد للسيارات",
    "status": "approved",
    "technician_id": "g0000000-0000-4000-8000-000000000001",
    "bank_account": {
      "bank_name": "البنك الأهلي",
      "account_holder": "أحمد الفني",
      "iban_masked": "SA03****7519",
      "is_verified": true
    },
    "payout_summary": {
      "total_earned_sar": 67.5,
      "pending_sar": 67.5,
      "released_sar": 0.0,
      "legs_count": 1
    }
  }
}
```

### الموافقة — `POST /api/v1/admin/vendors/{id}/approve`

```json
{
  "data": {
    "id": "...",
    "status": "approved",
    "technician_id": "g0000000-0000-4000-8000-000000000002"
  }
}
```

---

## قواعد العمل

1. **البريد والجوال** — فريدان على مستوى `vendors`.
2. **IBAN** — يبدأ بـ `SA` ويتبعه 22 رقمًا (تنسيق سعودي مبسّط).
3. **عند الموافقة** — إن وُجد فني بنفس رقم الجوال يُربَط؛ وإلا يُنشَأ سجل في `technicians`.
4. **المدفوعات** — تُجمع من `payment_split_legs` حيث `recipient_type = technician` و`recipient_id = technician_id`.
5. **تحديث المالية** — مسموح فقط للفنيين بحالة `approved`.

---

## لوحة الإدارة

```
rousto/admin/vendors.html
```

مراجعة الطلبات المعلّقة، الموافقة، والرفض — بنفس أسلوب لوحة الكتالوج.

---

## الملفات التنفيذية

```
rousto/backend/database/
├── 011_vendor_schema.sql
└── 012_vendor_seed.sql

rousto/backend/api/app/
├── vendor_services.py
└── routers/vendors.py

rousto/admin/
├── vendors.html
└── js/vendors.js
```

---

## الخطوة التالية

- [`10_VENDOR_MAP_LOCATION`](10_VENDOR_MAP_LOCATION.md) — خريطة وموقع الفني ✅
- `11_AUTH` — OTP + JWT + أدوار (`customer`, `technician`, `admin`)
