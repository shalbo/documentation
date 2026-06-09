// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class AppLocalizationsAr extends AppLocalizations {
  AppLocalizationsAr([String locale = 'ar']) : super(locale);

  @override
  String get appTitle => 'روستو';

  @override
  String get login => 'تسجيل الدخول';

  @override
  String get phoneNumber => 'رقم الجوال';

  @override
  String get verificationCode => 'رمز التحقق';

  @override
  String devOtpHelper(String otp) {
    return 'وضع التطوير: $otp';
  }

  @override
  String get codeSent => 'تم إرسال الرمز';

  @override
  String get confirmLogin => 'تأكيد الدخول';

  @override
  String get sendCode => 'إرسال الرمز';

  @override
  String get navHome => 'الرئيسية';

  @override
  String get navOrders => 'طلباتي';

  @override
  String get navOffers => 'عروض';

  @override
  String get navAccount => 'حسابي';

  @override
  String get welcomeBack => 'أهلاً بعودتك 👋';

  @override
  String get guest => 'ضيف';

  @override
  String get searchService => 'ابحث عن خدمة…';

  @override
  String get activeService => 'خدمة جارية';

  @override
  String get service => 'خدمة';

  @override
  String get popularServices => 'الخدمات الشائعة';

  @override
  String get viewAll => 'عرض الكل';

  @override
  String get pricingPlans => 'الأسعار والخطط';

  @override
  String get pricingPlansSubtitle => 'فردي · عائلي · أعمال — بالدينار';

  @override
  String get photoScan => 'فحص بالصورة';

  @override
  String get photoScanSubtitle => 'تشخيص مبدئي بالذكاء الاصطناعي';

  @override
  String get firstBookingDiscount => 'خصم على أول حجز';

  @override
  String useCode(String code) {
    return 'استخدم كود $code';
  }

  @override
  String get promoPercent => '٢٥٪';

  @override
  String get demoMode => 'وضع تجريبي';

  @override
  String get noActiveBooking => 'لا يوجد حجز جاري';

  @override
  String get refresh => 'تحديث';

  @override
  String get trackService => 'تتبّع الخدمة';

  @override
  String get messageTechnician => 'مراسلة الفني';

  @override
  String distanceKm(String distance) {
    return 'المسافة $distance كم';
  }

  @override
  String arrivesInMinutes(int minutes) {
    return 'يصل خلال $minutes دقيقة';
  }

  @override
  String distanceWithEta(String distance, int minutes) {
    return 'المسافة $distance كم · يصل خلال $minutes دقيقة';
  }

  @override
  String bookingStatusLine(String serviceName, String status) {
    return '$serviceName · $status';
  }

  @override
  String get offersAndSubscriptions => 'العروض والاشتراكات';

  @override
  String get fullPricingPage => 'صفحة الأسعار الكاملة';

  @override
  String get fullPricingSubtitle => 'خطط · باقات · أسعار الخدمات';

  @override
  String get yourPointsBalance => 'رصيد نقاطك';

  @override
  String get points => 'نقطة';

  @override
  String get point => 'نقطة';

  @override
  String pointsDiscountInfo(String discount, String amount) {
    return 'تكفي لخصم $discount — 100 نقطة = $amount';
  }

  @override
  String get membershipPlans => 'خطط العضوية';

  @override
  String get maintenancePackages => 'باقات الصيانة';

  @override
  String get redeemPoints => 'استبدال النقاط';

  @override
  String get exclusiveOffers => 'عروض حصرية';

  @override
  String get free => 'مجاني';

  @override
  String get subscribeNow => 'اشترك الآن';

  @override
  String get yourCurrentPlan => 'خطتك الحالية';

  @override
  String subscribedToPlan(String planName) {
    return 'تم الاشتراك في خطة $planName';
  }

  @override
  String get subscribeFailed => 'تعذّر الاشتراك — وضع تجريبي';

  @override
  String get redeem => 'استبدال';

  @override
  String get redeemFailed => 'تعذّر الاستبدال';

  @override
  String visitsSave(int visits, String savings) {
    return '$visits زيارات · وفّر $savings';
  }

  @override
  String pointsCost(int points) {
    return '$points نقطة';
  }

  @override
  String get confirmBooking => 'تأكيد الحجز';

  @override
  String get yourVehicle => 'سيارتك';

  @override
  String get appointment => 'الموعد';

  @override
  String get slotSaturday => 'السبت';

  @override
  String get slotSunday9am => 'الأحد 9 ص';

  @override
  String get slotMonday => 'الاثنين';

  @override
  String get slotTuesday => 'الثلاثاء';

  @override
  String get location => 'المكان';

  @override
  String get paymentMethod => 'طريقة الدفع';

  @override
  String get wallet => 'المحفظة';

  @override
  String get virtualCard => 'بطاقة افتراضية';

  @override
  String get serviceSummary => 'الخدمة';

  @override
  String get discountLabel => 'خصم (ROUSTO)';

  @override
  String get total => 'الإجمالي';

  @override
  String get paymentSplit => 'توزيع الدفع';

  @override
  String confirmAndPay(String amount) {
    return 'تأكيد ودفع $amount';
  }

  @override
  String get bookingConfirmed => 'تم تأكيد حجزك!';

  @override
  String get bookingSavedLocally => 'تم حفظ الحجز محلياً';

  @override
  String get bookingConfirmedDetail =>
      'سيتواصل معك فريق روستو لتأكيد التفاصيل.';

  @override
  String get bookingSavedDetail =>
      'تعذّر الاتصال بالخادم — تم الحفظ في الوضع التجريبي.';

  @override
  String get ok => 'تمام';

  @override
  String get noServicesAvailable => 'لا توجد خدمات متاحة';

  @override
  String get pricing => 'الأسعار';

  @override
  String get plansForEveryNeed => 'خطط تناسب كل احتياج';

  @override
  String get transparentPricing => 'أسعار شفافة بالدينار — تُحدَّث من الخادم';

  @override
  String get subscriptionPlans => 'خطط الاشتراك';

  @override
  String get servicePrices => 'أسعار الخدمات';

  @override
  String get whyRousto => 'لماذا روستو';

  @override
  String get aiScan => 'فحص بالصورة';

  @override
  String get artificialIntelligence => 'ذكاء اصطناعي';

  @override
  String get aiScanDescription =>
      'التقط صورة للمشكلة واحصل على تشخيص مبدئي وخدمة مقترحة';

  @override
  String get scanType => 'نوع الفحص';

  @override
  String get noImageSelected => 'لم تُختَر صورة بعد';

  @override
  String get chooseImage => 'اختيار صورة';

  @override
  String get analyzing => 'جاري التحليل...';

  @override
  String get analyzeImage => 'تحليل الصورة';

  @override
  String get scanResults => 'نتائج الفحص';

  @override
  String get analysisComplete => 'تم التحليل';

  @override
  String estimatedAccuracy(int percent) {
    return 'دقة تقديرية $percent٪';
  }

  @override
  String severity(String level) {
    return 'خطورة $level';
  }

  @override
  String get severityHigh => 'عالي';

  @override
  String get severityLow => 'منخفض';

  @override
  String get severityMedium => 'متوسط';

  @override
  String get suggestedService => 'الخدمة المقترحة';

  @override
  String bookService(String serviceName) {
    return 'احجز $serviceName';
  }

  @override
  String get notifications => 'الإشعارات';

  @override
  String get markAllRead => 'قراءة الكل';

  @override
  String unreadCount(int count) {
    return '$count غير مقروء';
  }

  @override
  String get noNotifications => 'لا توجد إشعارات';

  @override
  String get notificationPreferences => 'تفضيلات الإشعارات';

  @override
  String get inApp => 'داخل التطبيق';

  @override
  String get push => 'Push';

  @override
  String get savePreferences => 'حفظ التفضيلات';

  @override
  String get preferencesSaved => 'تم حفظ التفضيلات';

  @override
  String get onboardingTitle => 'عناية ذكية بسيارتك';

  @override
  String get onboardingSubtitle =>
      'احجز خدمة الصيانة في ثوانٍ وتابعها مباشرةً من هاتفك مع فنيّين معتمدين.';

  @override
  String get getStarted => 'ابدأ الآن';

  @override
  String get haveAccount => 'لديك حساب؟ ';

  @override
  String get settings => 'الإعدادات';

  @override
  String get settingsSubtitle => 'الإشعارات واللغة';

  @override
  String get myVehicles => 'سياراتي';

  @override
  String vehicleCount(int count) {
    return '$count مركبة';
  }

  @override
  String get orderHistory => 'سجل الطلبات';

  @override
  String get inventory => 'المخزون';

  @override
  String previousServicesCount(int count) {
    return '$count خدمة سابقة';
  }

  @override
  String get paymentMethods => 'طرق الدفع';

  @override
  String get paymentMethodsSubtitle => 'مدى، آبل باي';

  @override
  String get addresses => 'العناوين';

  @override
  String get addressesSubtitle => 'المنزل، العمل';

  @override
  String get rewards => 'المكافآت';

  @override
  String loyaltyPointsAvailable(int points) {
    return '$points نقطة متاحة';
  }

  @override
  String get supportAndSafety => 'الدعم والأمان';

  @override
  String get supportSubtitle => 'تذاكر الدعم والأسئلة الشائعة';

  @override
  String get serviceStat => 'خدمة';

  @override
  String get servicesStat => 'خدمات';

  @override
  String get vehicleStat => 'سيارة';

  @override
  String get vehiclesStat => 'سيارات';

  @override
  String get pointsStat => 'نقطة';

  @override
  String get savingsStat => 'توفير';

  @override
  String membership(String plan) {
    return 'عضوية $plan';
  }

  @override
  String membershipDiscount(int percent) {
    return ' · خصم $percent٪';
  }

  @override
  String get language => 'اللغة';

  @override
  String get arabic => 'العربية';

  @override
  String get english => 'English';

  @override
  String get legal => 'الوثائق القانونية';

  @override
  String get privacyPolicy => 'سياسة الخصوصية';

  @override
  String get termsOfService => 'شروط الخدمة';

  @override
  String get warrantyPolicy => 'ضمان الخدمة';

  @override
  String get connectionError => 'خطأ في الاتصال';

  @override
  String connectionErrorWithCode(int code) {
    return 'خطأ في الاتصال ($code)';
  }

  @override
  String get towingRequest => 'طلب سحب';

  @override
  String get privacyContent =>
      'Rousto Privacy Policy\n\nWe collect your phone number, vehicle information, and service history to provide automotive care services. Your data is encrypted in transit and stored securely. We do not sell personal data to third parties. Location data is used only during active service tracking. You may request data deletion by contacting support.\n\nContact: privacy@rousto.com';

  @override
  String get termsContent =>
      'Rousto Terms of Service\n\nBy using Rousto you agree to book services at listed prices, provide accurate vehicle information, and allow technicians access to perform requested work. Cancellations within 2 hours of appointment may incur a fee. Rousto acts as a platform connecting you with certified automotive service providers. Disputes are handled through in-app support.\n\nContact: legal@rousto.com';

  @override
  String get warrantyContent =>
      'Rousto Service Warranty\n\nServices booked through Rousto include a 7-day workmanship warranty on maintenance and repair work performed by certified technicians. Parts warranty follows manufacturer terms. Towing and emergency services are covered for the duration of the service session. To file a warranty claim, open a support ticket in the app with your booking reference.\n\nContact: warranty@rousto.com';

  @override
  String get privacyContentAr =>
      'سياسة الخصوصية — روستو\n\nنجمع رقم جوالك ومعلومات مركبتك وسجل الخدمات لتقديم خدمات العناية بالسيارات. بياناتك مشفّرة أثناء النقل ومخزّنة بأمان. لا نبيع البيانات الشخصية لأطراف ثالثة. بيانات الموقع تُستخدم فقط أثناء تتبّع الخدمة النشطة. يمكنك طلب حذف البيانات عبر الدعم.\n\nالتواصل: privacy@rousto.com';

  @override
  String get termsContentAr =>
      'شروط الخدمة — روستو\n\nباستخدام روستو فإنك توافق على حجز الخدمات بالأسعار المعلنة وتقديم معلومات دقيقة عن مركبتك والسماح للفنيين بإنجاز العمل المطلوب. الإلغاء خلال ساعتين من الموعد قد يترتب عليه رسوم. روستو منصة تربطك بمقدّمي خدمات سيارات معتمدين. النزاعات تُعالج عبر دعم التطبيق.\n\nالتواصل: legal@rousto.com';

  @override
  String get warrantyContentAr =>
      'ضمان الخدمة — روستو\n\nالخدمات المحجوزة عبر روستو تشمل ضمان إنجاز لمدة 7 أيام على أعمال الصيانة والإصلاح التي ينفّذها فنيون معتمدون. ضمان القطع يتبع شروط الشركة المصنّعة. السحب والخدمات الطارئة مغطاة طوال جلسة الخدمة. لرفع مطالبة ضمان، افتح تذكرة دعم في التطبيق مع رقم الحجز.\n\nالتواصل: warranty@rousto.com';

  @override
  String get unknownInitial => '؟';
}
