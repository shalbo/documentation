# روستو — Rousto Auto Care

واجهات الويب والتطبيق لمشروع **روستو** (منصة عناية ذكية بالسيارات)، مبنية على هوية
الشعار وألوانه (الأحمر القرمزي `#E11B22` على خلفية رمادية فاتحة `#F2F1ED`).

## المحتويات

```
rousto/
├── brand/                 # الهوية البصرية
│   ├── logo.svg           # الرمز (البادج)
│   ├── logo-wordmark.svg  # الشعار + الاسم
│   └── colors.md          # دليل الألوان والخطوط
├── docs/                  # مواصفات المشروع
│   ├── 01_DATABASE_SCHEMA.md
│   ├── 02_BACKEND_APIS.md
│   ├── 03_MOBILE_APP_UI.md
│   ├── 04_BUSINESS_MONETIZATION.md
│   ├── 05_ADMIN_CATALOG_MANAGEMENT.md
│   ├── 06_AI_AND_IMAGE_RECOGNITION.md
│   ├── 07_LOGISTICS_AND_LAST_MILE.md
│   ├── 08_SPLIT_PAYMENTS_ENGINE.md
│   ├── 09_VENDOR_ONBOARDING_FINANCIALS.md
│   ├── 10_VENDOR_MAP_LOCATION.md
│   ├── 11_CUSTOMER_DELIVERY_MAP.md
│   ├── 12_TOWING_DISPATCH_MAP.md
│   ├── 13_CUSTOMER_SUPPORT_AND_SECURITY.md
│   ├── 14_LANDING_PAGE_PRICING.md
│   ├── 15_FRONT_END_WEB.md
│   ├── 17_PERMISSIONS_AND_AUTH.md
│   ├── 18_ADVERTISING_AND_MARKETING_MODULE.md
│   ├── 19_PRODUCTION_HARDENING.md
│   └── 20_NOTIV.md
├── backend/               # قاعدة البيانات + REST API
│   ├── docker-compose.yml
│   ├── api/               # FastAPI
│   └── database/          # 001_schema.sql, 002_seed.sql
├── web/                   # موقع الويب + بوابة العميل (RTL)
│   ├── index.html         # صفحة الهبوط
│   ├── login.html         # تسجيل دخول OTP
│   ├── dashboard.html     # لوحة تحكم العميل
│   ├── booking.html       # حجز خدمة
│   ├── account.html       # حسابي
│   ├── css/               # theme, styles, portal
│   └── js/                # api, portal-layout, صفحات
├── app/                   # نموذج واجهات التطبيق بصيغة HTML (5 شاشات)
│   ├── index.html
│   └── css/app.css
├── admin/                 # لوحات الإدارة (كتالوج + تسويق + فنيين)
│   ├── index.html
│   ├── marketing.html
│   ├── vendors.html
│   ├── vendor-portal.html
│   ├── vendor-map.html
│   ├── css/admin.css
│   └── js/
└── app_flutter/           # تطبيق Flutter كامل (الإصدار الرسمي للتطبيق)
    ├── lib/               # الكود المصدري (شاشات، ثيم، مكوّنات)
    ├── web/               # غلاف الويب
    └── pubspec.yaml
```

> **تطبيق الجوال**: النسخة الرسمية مبنية بـ **Flutter** في `app_flutter/`
> (واجهة عربية RTL، 6 شاشات، تم التحقق منها عبر `flutter analyze` و`flutter test`).
> مجلد `app/` يحتوي على نموذج HTML أوّلي سريع للمعاينة فقط.

## التشغيل

كل شيء HTML/CSS/JS ثابت بدون أي اعتماديات. لتشغيله محلياً:

```bash
cd rousto
python3 -m http.server 8080
```

ثم افتح:
- موقع الويب: <http://localhost:8080/web/index.html>
- تسجيل الدخول: <http://localhost:8080/web/login.html>
- لوحة العميل: <http://localhost:8080/web/dashboard.html>
- الحجز: <http://localhost:8080/web/booking.html>
- حسابي: <http://localhost:8080/web/account.html>
- خريطة التوصيل: <http://localhost:8080/web/delivery-map.html>
- تتبّع السطحة: <http://localhost:8080/web/towing-map.html>
- الدعم والأمان: <http://localhost:8080/web/support.html>
- الإشعارات: <http://localhost:8080/web/notifications.html>
- صفحة الأسعار: <http://localhost:8080/web/pricing.html>
- نموذج التطبيق: <http://localhost:8080/app/index.html>

أو افتح ملفات `index.html` مباشرةً في المتصفح.

## المميزات

### موقع الويب
- واجهة عربية (RTL) متجاوبة بالكامل (جوال/لوحي/سطح المكتب).
- أقسام: البطل (Hero)، الخدمات، آلية العمل، لماذا روستو، نموذج الحجز، الإحصائيات،
  آراء العملاء، تنزيل التطبيق، التذييل.
- نموذج حجز تفاعلي، قائمة جوال، وحركات ظهور عند التمرير.

### نموذج التطبيق
خمس شاشات تعرض رحلة المستخدم بهوية الشعار:
1. شاشة الترحيب (Onboarding)
2. الرئيسية
3. تأكيد الحجز والدفع
4. التتبّع المباشر للفني
5. الملف الشخصي

## Backend (قاعدة البيانات + API)

```bash
cd rousto/backend && docker compose up -d
```

- قاعدة البيانات: PostgreSQL على المنفذ `5432`
- REST API: http://localhost:8000/docs
- لوحة الإدارة: http://localhost:8080/admin/index.html (بعد تشغيل `python3 -m http.server`)

المواصفات:
- [`docs/01_DATABASE_SCHEMA.md`](docs/01_DATABASE_SCHEMA.md)
- [`docs/02_BACKEND_APIS.md`](docs/02_BACKEND_APIS.md)
- [`docs/03_MOBILE_APP_UI.md`](docs/03_MOBILE_APP_UI.md)
- [`docs/04_BUSINESS_MONETIZATION.md`](docs/04_BUSINESS_MONETIZATION.md)
- [`docs/05_ADMIN_CATALOG_MANAGEMENT.md`](docs/05_ADMIN_CATALOG_MANAGEMENT.md)
- [`docs/06_AI_AND_IMAGE_RECOGNITION.md`](docs/06_AI_AND_IMAGE_RECOGNITION.md)
- [`docs/07_LOGISTICS_AND_LAST_MILE.md`](docs/07_LOGISTICS_AND_LAST_MILE.md)
- [`docs/08_SPLIT_PAYMENTS_ENGINE.md`](docs/08_SPLIT_PAYMENTS_ENGINE.md)
- [`docs/09_VENDOR_ONBOARDING_FINANCIALS.md`](docs/09_VENDOR_ONBOARDING_FINANCIALS.md)
- [`docs/10_VENDOR_MAP_LOCATION.md`](docs/10_VENDOR_MAP_LOCATION.md)
- [`docs/11_CUSTOMER_DELIVERY_MAP.md`](docs/11_CUSTOMER_DELIVERY_MAP.md)
- [`docs/12_TOWING_DISPATCH_MAP.md`](docs/12_TOWING_DISPATCH_MAP.md)
- [`docs/13_CUSTOMER_SUPPORT_AND_SECURITY.md`](docs/13_CUSTOMER_SUPPORT_AND_SECURITY.md)
- [`docs/14_LANDING_PAGE_PRICING.md`](docs/14_LANDING_PAGE_PRICING.md)
- [`docs/15_FRONT_END_WEB.md`](docs/15_FRONT_END_WEB.md)
- [`docs/17_PERMISSIONS_AND_AUTH.md`](docs/17_PERMISSIONS_AND_AUTH.md)
- [`docs/18_ADVERTISING_AND_MARKETING_MODULE.md`](docs/18_ADVERTISING_AND_MARKETING_MODULE.md)
- [`docs/19_PRODUCTION_HARDENING.md`](docs/19_PRODUCTION_HARDENING.md)

### تطبيق Flutter (متصل بالـ API)

```bash
cd rousto/backend && docker compose up -d
cd rousto/app_flutter && flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

## الهوية
انظر [`brand/colors.md`](brand/colors.md) لدليل الألوان والخطوط الكامل.
