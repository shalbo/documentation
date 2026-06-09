# 03 — واجهة تطبيق الجوال | Mobile App UI

تطبيق **Flutter** لمنصة روستو — عربي RTL، متصل بـ [REST API](02_BACKEND_APIS.md).

- **الإطار:** Flutter 3.x (Dart ≥3.0)
- **الخط:** Tajawal (Google Fonts)
- **الألوان:** `#E11B22` أحمر · `#F2F1ED` خلفية
- **الاتجاه:** RTL دائماً

---

## الشاشات (6)

| # | الشاشة | الملف | API |
|---|--------|-------|-----|
| 1 | الترحيب | `onboarding_screen.dart` | — |
| 2 | الرئيسية | `home_screen.dart` | `/categories/tree`, `/bookings/active`, `/me` |
| 3 | تأكيد الحجز | `booking_screen.dart` | `/me/*`, `/promotions/validate`, `POST /bookings` |
| 4 | التتبّع | `tracking_screen.dart` | `/bookings/active`, `/bookings/{id}/tracking` |
| 5 | العروض | `offers_screen.dart` | `/promotions`, `/me/loyalty` |
| 6 | الملف الشخصي | `profile_screen.dart` | `/me`, `/me/vehicles` |
| 7 | فحص بالصورة | `ai_scan_screen.dart` | `POST /scans`, `/scans/types` |
| 8 | نتائج الفحص | `scan_results_screen.dart` | `/scans/{id}` → الحجز |

التنقّل: `root_nav.dart` — شريط سفلي + FAB للحجز.

---

## البنية

```
app_flutter/lib/
├── main.dart
├── currency.dart                # تسمية العملة (دينار)
├── config/app_config.dart       # عنوان API + معرّف المستخدم
├── api/api_client.dart          # عميل HTTP
├── data/
│   ├── models.dart              # نماذج البيانات
│   ├── mock_data.dart           # بيانات احتياطية
│   └── app_repository.dart      # API مع fallback
├── state/app_state.dart         # حالة التطبيق (Provider)
├── theme/                       # ألوان وثيم
├── widgets/common.dart          # مكوّنات مشتركة
└── screens/                     # الشاشات الست
```

---

## ربط الـ API

| بيانات الشاشة | Endpoint | Fallback |
|---------------|----------|----------|
| تصنيفات + خدمات | `GET /categories/tree` | `MockData.categories` |
| اسم المستخدم | `GET /me` | سعود العتيبي |
| حجز جاري | `GET /bookings/active` | بطاقة ثابتة |
| تتبّع | `GET /bookings/{id}/tracking` | `MockData.trackSteps` |
| عروض | `GET /promotions` | قائمة ثابتة |
| نقاط | `GET /me/loyalty` | 320 نقطة |
| إنشاء حجز | `POST /bookings` | نجاح محلي |

### المصادقة (مؤقتة)

```
X-User-Id: a0000000-0000-4000-8000-000000000001
```

### عنوان الـ API

| المنصة | العنوان الافتراضي |
|--------|-------------------|
| Web / iOS Simulator | `http://localhost:8000` |
| Android Emulator | `http://10.0.2.2:8000` |

يُعدَّل عبر `--dart-define=API_BASE_URL=...`

---

## المكوّنات المشتركة

| المكوّن | الاستخدام |
|---------|-----------|
| `SoftCard` | بطاقات بيضاء بظل |
| `IconBadge` | أيقونة في مربّع ملوّن |
| `GradientButton` | زر أساسي أحمر |
| `RowHeader` | عنوان قسم |
| `LoadingOverlay` | حالة التحميل |
| `ErrorBanner` | خطأ مع إعادة المحاولة |

---

## حالات الواجهة

كل شاشة تدعم:
1. **تحميل** — `CircularProgressIndicator`
2. **بيانات** — عرض من API
3. **خطأ** — fallback للبيانات التجريبية + شارة "وضع تجريبي"
4. **فارغ** — رسالة مناسبة (مثلاً لا يوجد حجز جاري)

---

## التشغيل

```bash
cd rousto/backend && docker compose up -d   # تشغيل API + DB
cd rousto/app_flutter
flutter pub get
flutter run -d chrome \
  --dart-define=API_BASE_URL=http://localhost:8000
```

---

## الاختبارات

```bash
flutter analyze
flutter test
```

---

## الخطوة التالية

- [`04_BUSINESS_MONETIZATION`](04_BUSINESS_MONETIZATION.md) — اشتراكات، باقات، استبدال نقاط ✅
- [`05_ADMIN_CATALOG_MANAGEMENT`](05_ADMIN_CATALOG_MANAGEMENT.md) — لوحة إدارة الكتالوج ✅
- [`06_AI_AND_IMAGE_RECOGNITION`](06_AI_AND_IMAGE_RECOGNITION.md) — فحص بالصورة ✅
- [`07_LOGISTICS_AND_LAST_MILE`](07_LOGISTICS_AND_LAST_MILE.md) — تتبّع مباشر + خريطة نسبية ✅
- `08_AUTH` — OTP + JWT (استبدال `X-User-Id`)
