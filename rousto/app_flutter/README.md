# تطبيق روستو (Flutter)

تطبيق **روستو للعناية الذكية بالسيارات** مبني بـ Flutter بهوية الشعار وألوانه
(الأحمر القرمزي `#E11B22` على خلفية رمادية فاتحة `#F2F1ED`)، بواجهة عربية (RTL).

## الشاشات
1. **الترحيب** (`onboarding_screen.dart`) — شعار على خلفية داكنة متدرّجة.
2. **الرئيسية** (`home_screen.dart`) — ترويسة حمراء، خدمة جارية، تصنيفات، شبكة خدمات، عرض ترويجي.
3. **تأكيد الحجز** (`booking_screen.dart`) — تفاصيل الخدمة والموعد والدفع وملخّص الفاتورة.
4. **التتبّع المباشر** (`tracking_screen.dart`) — خريطة، بطاقة الفني، وخط زمني للحالة.
5. **العروض** (`offers_screen.dart`) — رصيد النقاط والعروض الحصرية.
6. **الملف الشخصي** (`profile_screen.dart`) — إحصائيات وقائمة الإعدادات.

التنقّل عبر شريط سفلي مع زر عائم مركزي (FAB) للحجز السريع.

## البنية
```
app_flutter/
├── pubspec.yaml
├── analysis_options.yaml
├── assets/                 # شعارات SVG
└── lib/
    ├── main.dart           # التطبيق + RTL + الثيم
    ├── theme/              # الألوان (app_colors) والثيم (app_theme)
    ├── data/models.dart    # النماذج والبيانات التجريبية
    ├── widgets/common.dart # مكوّنات مشتركة (أزرار، بطاقات، شارات)
    └── screens/            # الشاشات
```

## التشغيل
```bash
cd rousto/app_flutter
flutter pub get
flutter run            # على محاكي/جهاز
# أو للويب:
flutter run -d chrome
```

## الاعتماديات
- `flutter_svg` — عرض شعار SVG.
- `google_fonts` — خط Tajawal العربي.
- `flutter_localizations` — دعم اللغة العربية و RTL.

> هذا التطبيق هو نسخة Flutter من النموذج، إلى جانب نموذج HTML في `../app/`.
