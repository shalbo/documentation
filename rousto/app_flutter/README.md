# تطبيق روستو (Flutter)

تطبيق **روستو للعناية الذكية بالسيارات** — واجهة عربية RTL متصلة بـ REST API.

المواصفات: [`../docs/03_MOBILE_APP_UI.md`](../docs/03_MOBILE_APP_UI.md)

## الشاشات
1. **الترحيب** — شعار + بدء
2. **الرئيسية** — تصنيفات، خدمات، حجز جاري (من `/categories/tree`)
3. **تأكيد الحجز** — سيارة، موعد، دفع (`POST /bookings`)
4. **التتبّع** — خريطة، فني، خط زمني (`/bookings/{id}/tracking`)
5. **العروض** — نقاط وعروض (`/promotions`, `/me/loyalty`)
6. **الملف الشخصي** — إحصائيات (`/me`)

## البنية
```
lib/
├── config/app_config.dart
├── api/api_client.dart
├── data/models.dart, mock_data.dart, app_repository.dart
├── state/app_state.dart
├── theme/, widgets/, screens/
```

## التشغيل

```bash
# 1) شغّل الـ Backend
cd ../backend && docker compose up -d

# 2) شغّل التطبيق
cd rousto/app_flutter
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

بدون API يعمل التطبيق في **وضع تجريبي** (بيانات Mock) مع شارة "وضع تجريبي".

## الاختبارات
```bash
flutter analyze
flutter test
```

## الاعتماديات
- `provider` — إدارة الحالة
- `http` — عميل API
- `flutter_svg`, `google_fonts` — الشعار والخط
