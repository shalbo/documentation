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
│   └── 06_AI_AND_IMAGE_RECOGNITION.md
├── backend/               # قاعدة البيانات + REST API
│   ├── docker-compose.yml
│   ├── api/               # FastAPI
│   └── database/          # 001_schema.sql, 002_seed.sql
├── web/                   # موقع الويب (متجاوب، RTL)
│   ├── index.html
│   ├── css/theme.css      # نظام التصميم (المتغيرات)
│   ├── css/styles.css     # مكوّنات الموقع
│   └── js/main.js         # التفاعلات (القائمة، الكشف عند التمرير، النموذج)
├── app/                   # نموذج واجهات التطبيق بصيغة HTML (5 شاشات)
│   ├── index.html
│   └── css/app.css
├── admin/                 # لوحة إدارة الكتالوج (تصنيفات + خدمات)
│   ├── index.html
│   ├── css/admin.css
│   └── js/admin.js
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

### تطبيق Flutter (متصل بالـ API)

```bash
cd rousto/backend && docker compose up -d
cd rousto/app_flutter && flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

## الهوية
انظر [`brand/colors.md`](brand/colors.md) لدليل الألوان والخطوط الكامل.
