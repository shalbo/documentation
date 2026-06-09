# 02 — واجهات الـ Backend | Backend APIs

REST API لمنصة **روستو** مبنية على [مخطط قاعدة البيانات](01_DATABASE_SCHEMA.md).

- **الإطار:** FastAPI (Python 3.12+)
- **قاعدة البيانات:** PostgreSQL 16
- **الإصدار:** `v1`
- **الأساس:** `/api/v1`
- **التوثيق التفاعلي:** `/docs` (Swagger) · `/redoc`

---

## المصادقة

انظر [`17_PERMISSIONS_AND_AUTH`](17_PERMISSIONS_AND_AUTH.md).

### JWT (مفضّل)

```
Authorization: Bearer <access_token>
```

احصل على التوكن عبر `POST /api/v1/auth/otp/verify` بعد إرسال OTP.

### توافق خلفي (تطوير)

```
X-User-Id: a0000000-0000-4000-8000-000000000001
X-Admin-Key: rousto_admin_dev
X-Vendor-Id: v0000000-0000-4000-8000-000000000001
```

| المستخدم | الجوال | الأدوار |
|----------|--------|---------|
| سعود العتيبي | `+966501234567` | customer, admin |
| أحمد فني | `+966509876543` | technician |

وضع التطوير: `OTP_DEV_MODE=true` يُرجع الرمز `123456` في `meta.dev_otp`.

---

## الاستجابات

### نجاح

```json
{
  "data": { ... }
}
```

### قائمة

```json
{
  "data": [ ... ],
  "meta": { "total": 6 }
}
```

### خطأ

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "الحجز غير موجود"
  }
}
```

| HTTP | المعنى |
|------|--------|
| 200 | نجاح |
| 201 | تم الإنشاء |
| 400 | بيانات غير صالحة |
| 401 | غير مصرّح |
| 404 | غير موجود |
| 422 | فشل التحقق |

---

## النقاط الطرفية (Endpoints)

### الصحة

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/health` | فحص الخدمة وقاعدة البيانات | لا |

---

### المصادقة والصلاحيات

انظر [`17_PERMISSIONS_AND_AUTH`](17_PERMISSIONS_AND_AUTH.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| POST | `/api/v1/auth/otp/send` | إرسال رمز OTP | لا |
| POST | `/api/v1/auth/otp/verify` | التحقق وإصدار JWT | لا |
| POST | `/api/v1/auth/refresh` | تجديد access token | لا |
| POST | `/api/v1/auth/logout` | إلغاء refresh token | لا |
| GET | `/api/v1/auth/me` | المستخدم + الأدوار + الصلاحيات | JWT |
| GET | `/api/v1/auth/permissions` | قائمة الصلاحيات | Admin |
| GET | `/api/v1/auth/roles` | قائمة الأدوار | لا |
| GET | `/api/v1/admin/auth/users/{id}/roles` | أدوار مستخدم | Admin |
| PUT | `/api/v1/admin/auth/users/{id}/roles` | تعيين أدوار | Admin |

---

### الكتالوج (عام)

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/categories` | تصنيفات الخدمات | لا |
| GET | `/api/v1/categories/tree` | شجرة التصنيفات + الخدمات المتداخلة | لا |
| GET | `/api/v1/services` | قائمة الخدمات (`?category=oil`) | لا |
| GET | `/api/v1/services/{id}` | تفاصيل خدمة | لا |

---

### الفحص بالصورة (AI)

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/scans/types` | أنواع الفحص المتاحة | لا |
| POST | `/api/v1/scans` | رفع صور وتحليل (multipart) | نعم |
| GET | `/api/v1/scans/{id}` | تفاصيل فحص | نعم |
| GET | `/api/v1/me/scans` | سجل فحوصات المستخدم | نعم |

انظر [`06_AI_AND_IMAGE_RECOGNITION`](06_AI_AND_IMAGE_RECOGNITION.md).

---

### الكتالوج (إدارة)

> يتطلب هيدر `X-Admin-Key` — انظر [`05_ADMIN_CATALOG_MANAGEMENT`](05_ADMIN_CATALOG_MANAGEMENT.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/admin/categories` | كل التصنيفات | Admin |
| POST | `/api/v1/admin/categories` | إنشاء تصنيف | Admin |
| PATCH | `/api/v1/admin/categories/{id}` | تعديل تصنيف | Admin |
| POST | `/api/v1/admin/categories/reorder` | إعادة ترتيب | Admin |
| GET | `/api/v1/admin/services` | كل الخدمات | Admin |
| POST | `/api/v1/admin/services` | إنشاء خدمة | Admin |
| PATCH | `/api/v1/admin/services/{id}` | تعديل خدمة | Admin |

**مثال — `GET /api/v1/categories/tree`**

```json
{
  "data": [
    {
      "id": "e0000000-0000-4000-8000-000000000001",
      "slug": "all",
      "name_ar": "الكل",
      "sort_order": 0,
      "services_count": 6,
      "services": [
        {
          "id": "f0000000-0000-4000-8000-000000000001",
          "slug": "oil-change",
          "name_ar": "تغيير الزيت والفلاتر",
          "subtitle_ar": "زيت أصلي + فحص شامل",
          "icon_key": "oil_barrel",
          "price_sar": 120.0,
          "duration_minutes": 45
        }
      ]
    }
  ],
  "meta": { "total_categories": 6, "total_services": 6 }
}
```

انظر [`GET_api_v1_categories_tree.md`](GET_api_v1_categories_tree.md) للمواصفات الكاملة.

**مثال — `GET /api/v1/services`**

```json
{
  "data": [
    {
      "id": "f0000000-0000-4000-8000-000000000001",
      "slug": "oil-change",
      "name_ar": "تغيير الزيت والفلاتر",
      "subtitle_ar": "زيت أصلي + فحص شامل",
      "icon_key": "oil_barrel",
      "price_sar": 120.0,
      "duration_minutes": 45,
      "category": { "slug": "oil", "name_ar": "زيت" }
    }
  ],
  "meta": { "total": 6 }
}
```

---

### الملف الشخصي

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/me` | بيانات المستخدم | نعم |
| GET | `/api/v1/me/vehicles` | سياراتي | نعم |
| GET | `/api/v1/me/addresses` | عناويني | نعم |
| GET | `/api/v1/me/payment-methods` | طرق الدفع | نعم |
| GET | `/api/v1/me/loyalty` | رصيد النقاط وآخر الحركات | نعم |

**مثال — `GET /api/v1/me`**

```json
{
  "data": {
    "id": "a0000000-0000-4000-8000-000000000001",
    "full_name": "سعود العتيبي",
    "email": "saud@example.com",
    "phone": "+966501234567",
    "avatar_initials": "س",
    "loyalty_points": 320,
    "stats": { "services_count": 14, "vehicles_count": 2 }
  }
}
```

---

### الحجوزات

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/bookings` | سجل حجوزاتي | نعم |
| GET | `/api/v1/bookings/active` | الحجز الجاري (للتتبّع) | نعم |
| GET | `/api/v1/bookings/{id}` | تفاصيل حجز | نعم |
| GET | `/api/v1/bookings/{id}/tracking` | خط زمني التتبّع + الفني | نعم |
| GET | `/api/v1/bookings/{id}/delivery-map` | خريطة توصيل غنية (مسار + تقدّم) | نعم |
| GET | `/api/v1/bookings/active/delivery-map` | خريطة الحجز النشط | نعم |
| POST | `/api/v1/bookings` | إنشاء حجز جديد | نعم |

**إنشاء حجز — `POST /api/v1/bookings`**

```json
{
  "service_id": "f0000000-0000-4000-8000-000000000001",
  "vehicle_id": "b0000000-0000-4000-8000-000000000001",
  "address_id": "c0000000-0000-4000-8000-000000000001",
  "payment_method_id": "d0000000-0000-4000-8000-000000000001",
  "promotion_code": "ROUSTO",
  "scheduled_at": "2026-06-10T09:00:00+03:00",
  "notes": null
}
```

**استجابة التتبّع — `GET /api/v1/bookings/{id}/tracking`**

```json
{
  "data": {
    "booking": {
      "reference": "RST-2026-001",
      "status": "en_route",
      "status_label_ar": "جارية"
    },
    "technician": {
      "full_name": "أحمد الفني",
      "phone": "+966509876543",
      "rating": 4.9,
      "avatar_initials": "أ",
      "eta_minutes": 2,
      "location": { "lat": 24.77, "lng": 46.735 }
    },
    "destination": {
      "label": "المنزل · حي النخيل",
      "lat": 24.774265,
      "lng": 46.738586
    },
    "distance_km": 0.42,
    "eta_minutes": 2,
    "steps": [
      { "status": "confirmed", "label_ar": "تم تأكيد الحجز", "occurred_at": "...", "is_current": false, "is_done": true },
      { "status": "en_route", "label_ar": "الفني في الطريق إليك", "occurred_at": "...", "is_current": true, "is_done": false },
      { "status": "in_progress", "label_ar": "جاري تنفيذ الخدمة", "occurred_at": null, "is_current": false, "is_done": false }
    ]
  }
}
```

---

### تقسيم المدفوعات

انظر [`08_SPLIT_PAYMENTS_ENGINE`](08_SPLIT_PAYMENTS_ENGINE.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/payments/split-rules` | قواعد التقسيم | لا |
| POST | `/api/v1/payments/split/preview` | معاينة التقسيم | لا |
| GET | `/api/v1/bookings/{id}/payment-split` | تفاصيل تقسيم حجز | نعم |
| POST | `/api/v1/payments/splits/release` | إطلاق حصة معلّقة | Admin |

---

### انضمام الفنيين والمالية

انظر [`09_VENDOR_ONBOARDING_FINANCIALS`](09_VENDOR_ONBOARDING_FINANCIALS.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| POST | `/api/v1/vendors/applications` | تقديم طلب انضمام | لا |
| GET | `/api/v1/vendor/me` | ملف الفني + ملخص المدفوعات | Vendor |
| PUT | `/api/v1/vendor/me/financials` | تحديث IBAN | Vendor |
| GET | `/api/v1/vendor/me/payouts` | حصص الدفع | Vendor |
| GET | `/api/v1/admin/vendors` | قائمة الطلبات | Admin |
| POST | `/api/v1/admin/vendors/{id}/approve` | الموافقة | Admin |
| POST | `/api/v1/admin/vendors/{id}/reject` | الرفض | Admin |

**مصادقة مؤقتة:** `X-Vendor-Id: v0000000-0000-4000-8000-000000000001` (فني seed مُوافَق).

---

### بوابة عميل الويب

انظر [`15_FRONT_END_WEB`](15_FRONT_END_WEB.md).

الصفحات تستهلك نفس الـ API عبر `web/js/api.js` — JWT من `login.html` أو `X-User-Id` للتطوير.

| الصفحة | Endpoints المستخدمة |
|--------|---------------------|
| `dashboard.html` | `/me`, `/bookings/active` |
| `booking.html` | `/categories/tree`, `/me/*`, `POST /bookings` |
| `account.html` | `/me`, `/me/vehicles`, `/bookings`, `/me/monetization` |

---

### صفحة الهبوط والأسعار

انظر [`14_LANDING_PAGE_PRICING`](14_LANDING_PAGE_PRICING.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/landing/pricing` | خدمات + خطط تسويقية + اشتراكات + باقات | لا |
| GET | `/api/v1/landing/page` | بيانات صفحة الهبوط (hero + pricing + features + marketing) | لا |

---

### الإعلانات والتسويق

انظر [`18_ADVERTISING_AND_MARKETING_MODULE`](18_ADVERTISING_AND_MARKETING_MODULE.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/marketing/banners` | بانرات نشطة (`?placement=`) | لا |
| GET | `/api/v1/marketing/partners` | شركاء العلامات | لا |
| GET | `/api/v1/marketing/campaigns` | حملات نشطة | لا |
| POST | `/api/v1/marketing/newsletter/subscribe` | اشتراك نشرة | لا |
| POST | `/api/v1/marketing/attribution/track` | تتبّع UTM | لا |
| GET | `/api/v1/marketing/referrals/validate` | التحقق من كود إحالة | لا |
| GET | `/api/v1/me/referral` | كود الإحالة الخاص بي | Customer |
| POST | `/api/v1/me/referral` | إنشاء كود إحالة | Customer |
| GET/POST/PATCH | `/api/v1/admin/promotions` | إدارة أكواد الخصم | Admin |
| GET/POST/PATCH | `/api/v1/admin/marketing/*` | حملات، بانرات، شركاء | Admin |
| GET | `/api/v1/admin/marketing/analytics` | ملخص إحصائي | Admin |

---

### الإشعارات (NOTIV)

انظر [`20_NOTIV`](20_NOTIV.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/me/notifications` | صندوق الإشعارات (`?unread_only=&category=`) | Customer |
| GET | `/api/v1/me/notifications/unread-count` | عدد غير المقروء | Customer |
| PATCH | `/api/v1/me/notifications/{id}/read` | تعليم كمقروء | Customer |
| POST | `/api/v1/me/notifications/read-all` | تعليم الكل مقروء | Customer |
| GET | `/api/v1/me/notification-preferences` | تفضيلات الفئات | Customer |
| PUT | `/api/v1/me/notification-preferences` | تحديث التفضيلات | Customer |
| POST | `/api/v1/me/devices/register` | تسجيل FCM token | Customer |
| GET | `/api/v1/admin/notifications` | سجل الإشعارات | Admin |
| POST | `/api/v1/admin/notifications/send` | إرسال إشعار لمستخدم | Admin |

---

### دعم العملاء والأمان

انظر [`13_CUSTOMER_SUPPORT_AND_SECURITY`](13_CUSTOMER_SUPPORT_AND_SECURITY.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/support/faq` | الأسئلة الشائعة | لا |
| POST | `/api/v1/support/tickets` | فتح تذكرة | Customer |
| GET | `/api/v1/support/tickets` | تذاكري | Customer |
| GET | `/api/v1/support/tickets/{id}` | تفاصيل التذكرة | Customer |
| POST | `/api/v1/support/tickets/{id}/messages` | رد العميل | Customer |
| GET | `/api/v1/me/security` | ملخص الأمان | Customer |
| POST | `/api/v1/me/security/report` | إبلاغ نشاط مشبوه | Customer |
| GET | `/api/v1/admin/support/tickets` | كل التذاكر | Admin |
| POST | `/api/v1/admin/support/tickets/{id}/reply` | رد الإدارة | Admin |
| GET | `/api/v1/admin/security/events` | سجل الأحداث | Admin |

---

### إرسال السطحات

انظر [`12_TOWING_DISPATCH_MAP`](12_TOWING_DISPATCH_MAP.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| POST | `/api/v1/towing/dispatches` | إنشاء طلب سحب | Customer |
| GET | `/api/v1/towing/dispatches/{id}/map` | خريطة الإرسال | Customer |
| GET | `/api/v1/towing/dispatches/active/map` | خريطة الطلب النشط | Customer |
| GET | `/api/v1/admin/towing/dispatches` | قائمة الإرسالات | Admin |
| GET | `/api/v1/admin/towing/dispatches/map` | خريطة كل الإرسالات | Admin |
| POST | `/api/v1/admin/towing/dispatches/{id}/dispatch` | تعيين سائق | Admin |
| POST | `/api/v1/admin/towing/dispatches/{id}/advance` | التقدّم للمرحلة التالية | Admin |
| PATCH | `/api/v1/admin/towing/dispatches/{id}/location` | تحديث GPS السطحة | Admin |

---

### خريطة توصيل العميل

انظر [`11_CUSTOMER_DELIVERY_MAP`](11_CUSTOMER_DELIVERY_MAP.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/bookings/{id}/delivery-map` | فني + عميل + مسار + تقدّم % | Customer |
| GET | `/api/v1/bookings/active/delivery-map` | خريطة الحجز الجاري | Customer |

---

### خريطة وموقع الفني

انظر [`10_VENDOR_MAP_LOCATION`](10_VENDOR_MAP_LOCATION.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/vendor/me/map` | خريطة كاملة + مهمة نشطة | Vendor |
| PUT | `/api/v1/vendor/me/location/base` | موقع القاعدة ونطاق التغطية | Vendor |
| PATCH | `/api/v1/vendor/me/location/live` | تحديث GPS المباشر | Vendor |
| GET | `/api/v1/vendor/me/jobs/active` | المهمة النشطة | Vendor |
| PATCH | `/api/v1/vendor/me/availability` | تبديل التوفر | Vendor |
| GET | `/api/v1/admin/vendors/map` | خريطة كل الفنيين | Admin |

---

### اللوجستيات (dev/admin)

انظر [`07_LOGISTICS_AND_LAST_MILE`](07_LOGISTICS_AND_LAST_MILE.md).

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| POST | `/api/v1/logistics/bookings/{id}/advance` | الحالة التالية | Admin |
| PATCH | `/api/v1/logistics/technicians/{id}/location` | تحديث GPS | Admin |
| POST | `/api/v1/logistics/bookings/{id}/simulate-move` | تحريك تجريبي | Admin |

---

### العروض

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/promotions` | العروض النشطة | لا |
| POST | `/api/v1/promotions/validate` | التحقق من كود خصم | نعم |

**التحقق — `POST /api/v1/promotions/validate`**

```json
{ "code": "ROUSTO", "service_price_sar": 120.0 }
```

```json
{
  "data": {
    "valid": true,
    "discount_sar": 30.0,
    "total_sar": 90.0,
    "promotion": { "code": "ROUSTO", "title_ar": "خصم 25٪ على أول حجز" }
  }
}
```

---

### آراء العملاء

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/testimonials` | آراء منشورة | لا |

---

### تحقيق الدخل

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/monetization/plans` | خطط الاشتراك | لا |
| GET | `/api/v1/monetization/packages` | باقات الصيانة | لا |
| GET | `/api/v1/monetization/rewards` | مكافآت النقاط | لا |
| GET | `/api/v1/me/monetization` | ملخص المحفظة | نعم |
| POST | `/api/v1/me/membership/subscribe` | الاشتراك في خطة | نعم |
| POST | `/api/v1/me/loyalty/redeem` | استبدال نقاط | نعم |

انظر [`04_BUSINESS_MONETIZATION.md`](04_BUSINESS_MONETIZATION.md).

---

## هيكل المشروع

```
rousto/backend/api/
├── app/
│   ├── main.py          # نقطة الدخول + CORS
│   ├── config.py        # إعدادات البيئة
│   ├── db.py            # SQLAlchemy + الجلسة
│   ├── deps.py          # JWT + RBAC + توافق خلفي
│   ├── auth_services.py # OTP + JWT
│   ├── permissions.py   # أدوار وصلاحيات
│   ├── models.py        # نماذج ORM
│   ├── schemas.py       # Pydantic
│   └── routers/         # health, catalog, profile, bookings, promotions, testimonials
├── requirements.txt
├── Dockerfile
└── tests/
```

---

## التشغيل

```bash
cd rousto/backend
docker compose up -d          # PostgreSQL + API
curl http://localhost:8000/api/v1/health
open http://localhost:8000/docs
```

### محلياً (بدون Docker للـ API)

```bash
cd rousto/backend/api
pip install -r requirements.txt
DATABASE_URL=postgresql://rousto:rousto_dev@localhost:5432/rousto \
  uvicorn app.main:app --reload --port 8000
```

### مثال طلب

```bash
# OTP + JWT
curl -X POST http://localhost:8000/api/v1/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{"phone":"+966501234567"}'

curl -X POST http://localhost:8000/api/v1/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"phone":"+966501234567","code":"123456"}'

# أو توافق خلفي
curl -H "X-User-Id: a0000000-0000-4000-8000-000000000001" \
  http://localhost:8000/api/v1/bookings/active
```

---

## الخطوة التالية

- [`03_MOBILE_APP_UI`](../docs/03_MOBILE_APP_UI.md) — تطبيق Flutter المتصل بالـ API ✅
- [`04_BUSINESS_MONETIZATION`](../docs/04_BUSINESS_MONETIZATION.md) — تحقيق الدخل والاشتراكات ✅
- [`05_ADMIN_CATALOG_MANAGEMENT`](../docs/05_ADMIN_CATALOG_MANAGEMENT.md) — إدارة الكتالوج + لوحة الويب ✅
- [`06_AI_AND_IMAGE_RECOGNITION`](../docs/06_AI_AND_IMAGE_RECOGNITION.md) — فحص بالصورة + تشخيص تجريبي ✅
- [`07_LOGISTICS_AND_LAST_MILE`](../docs/07_LOGISTICS_AND_LAST_MILE.md) — توصيل الخدمة + ETA + تتبّع مباشر ✅
- [`08_SPLIT_PAYMENTS_ENGINE`](../docs/08_SPLIT_PAYMENTS_ENGINE.md) — محرك تقسيم المدفوعات ✅
- [`09_VENDOR_ONBOARDING_FINANCIALS`](../docs/09_VENDOR_ONBOARDING_FINANCIALS.md) — انضمام الفنيين والمالية ✅
- [`10_VENDOR_MAP_LOCATION`](../docs/10_VENDOR_MAP_LOCATION.md) — خريطة وموقع الفني ✅
- [`11_CUSTOMER_DELIVERY_MAP`](../docs/11_CUSTOMER_DELIVERY_MAP.md) — خريطة توصيل العميل ✅
- [`12_TOWING_DISPATCH_MAP`](../docs/12_TOWING_DISPATCH_MAP.md) — خريطة إرسال السطحات ✅
- [`13_CUSTOMER_SUPPORT_AND_SECURITY`](../docs/13_CUSTOMER_SUPPORT_AND_SECURITY.md) — دعم العملاء والأمان ✅
- [`14_LANDING_PAGE_PRICING`](../docs/14_LANDING_PAGE_PRICING.md) — صفحة الهبوط والأسعار ✅
- [`15_FRONT_END_WEB`](../docs/15_FRONT_END_WEB.md) — بوابة عميل الويب ✅
- [`17_PERMISSIONS_AND_AUTH`](../docs/17_PERMISSIONS_AND_AUTH.md) — OTP + JWT + أدوار وصلاحيات ✅
- [`18_ADVERTISING_AND_MARKETING_MODULE`](../docs/18_ADVERTISING_AND_MARKETING_MODULE.md) — حملات وبانرات وإحالات ✅
- [`20_NOTIV`](../docs/20_NOTIV.md) — صندوق إشعارات in-app + FCM push ✅
