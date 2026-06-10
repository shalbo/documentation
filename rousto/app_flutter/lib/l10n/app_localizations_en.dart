// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Rousto';

  @override
  String get login => 'Login';

  @override
  String get phoneNumber => 'Phone Number';

  @override
  String get verificationCode => 'Verification Code';

  @override
  String devOtpHelper(String otp) {
    return 'Development mode: $otp';
  }

  @override
  String get codeSent => 'Code sent';

  @override
  String get confirmLogin => 'Confirm Login';

  @override
  String get sendCode => 'Send Code';

  @override
  String get navHome => 'Home';

  @override
  String get navOrders => 'My Requests';

  @override
  String get navOffers => 'Offers';

  @override
  String get navAccount => 'Account';

  @override
  String get welcomeBack => 'Welcome back 👋';

  @override
  String get guest => 'Guest';

  @override
  String get searchService => 'Search for a service…';

  @override
  String get activeService => 'Active Service';

  @override
  String get service => 'Service';

  @override
  String get popularServices => 'Popular Services';

  @override
  String get viewAll => 'View All';

  @override
  String get pricingPlans => 'Pricing & Plans';

  @override
  String get pricingPlansSubtitle =>
      'Individual · Family · Business — in Dinar';

  @override
  String get photoScan => 'Photo Scan';

  @override
  String get photoScanSubtitle => 'AI preliminary diagnosis';

  @override
  String get firstBookingDiscount => 'First booking discount';

  @override
  String useCode(String code) {
    return 'Use code $code';
  }

  @override
  String get promoPercent => '25%';

  @override
  String get demoMode => 'Demo mode';

  @override
  String get noActiveBooking => 'No active booking';

  @override
  String get refresh => 'Refresh';

  @override
  String get trackService => 'Tracking';

  @override
  String get messageTechnician => 'Message Technician';

  @override
  String distanceKm(String distance) {
    return 'Distance $distance km';
  }

  @override
  String arrivesInMinutes(int minutes) {
    return 'Arrives in $minutes min';
  }

  @override
  String distanceWithEta(String distance, int minutes) {
    return 'Distance $distance km · Arrives in $minutes min';
  }

  @override
  String bookingStatusLine(String serviceName, String status) {
    return '$serviceName · $status';
  }

  @override
  String get offersAndSubscriptions => 'Offers & Subscriptions';

  @override
  String get fullPricingPage => 'Full Pricing Page';

  @override
  String get fullPricingSubtitle => 'Plans · Packages · Service Prices';

  @override
  String get yourPointsBalance => 'Your Points Balance';

  @override
  String get points => 'points';

  @override
  String get point => 'point';

  @override
  String pointsDiscountInfo(String discount, String amount) {
    return 'Enough for $discount off — 100 points = $amount';
  }

  @override
  String get membershipPlans => 'Membership Plans';

  @override
  String get maintenancePackages => 'Maintenance Packages';

  @override
  String get redeemPoints => 'Redeem Points';

  @override
  String get exclusiveOffers => 'Exclusive Offers';

  @override
  String get free => 'Free';

  @override
  String get subscribeNow => 'Subscribe Now';

  @override
  String get yourCurrentPlan => 'Your Current Plan';

  @override
  String subscribedToPlan(String planName) {
    return 'Subscribed to $planName plan';
  }

  @override
  String get subscribeFailed => 'Subscription failed — demo mode';

  @override
  String get redeem => 'Redeem';

  @override
  String get redeemFailed => 'Redemption failed';

  @override
  String visitsSave(int visits, String savings) {
    return '$visits visits · Save $savings';
  }

  @override
  String pointsCost(int points) {
    return '$points points';
  }

  @override
  String get confirmBooking => 'Confirm Booking';

  @override
  String get yourVehicle => 'Your Vehicle';

  @override
  String get appointment => 'Appointment';

  @override
  String get slotSaturday => 'Saturday';

  @override
  String get slotSunday9am => 'Sunday 9 AM';

  @override
  String get slotMonday => 'Monday';

  @override
  String get slotTuesday => 'Tuesday';

  @override
  String get location => 'Location';

  @override
  String get paymentMethod => 'Payment Method';

  @override
  String get wallet => 'Wallet';

  @override
  String get virtualCard => 'Virtual card';

  @override
  String get serviceSummary => 'Service';

  @override
  String get discountLabel => 'Discount (ROUSTO)';

  @override
  String get total => 'Total';

  @override
  String get paymentSplit => 'Payment Split';

  @override
  String confirmAndPay(String amount) {
    return 'Confirm & Pay $amount';
  }

  @override
  String get bookingConfirmed => 'Booking confirmed!';

  @override
  String get bookingSavedLocally => 'Booking saved locally';

  @override
  String get bookingConfirmedDetail =>
      'The Rousto team will contact you to confirm details.';

  @override
  String get bookingSavedDetail =>
      'Could not reach server — saved in demo mode.';

  @override
  String get ok => 'OK';

  @override
  String get noServicesAvailable => 'No services available';

  @override
  String get pricing => 'Pricing';

  @override
  String get plansForEveryNeed => 'Plans for every need';

  @override
  String get transparentPricing =>
      'Transparent pricing in Dinar — updated from server';

  @override
  String get subscriptionPlans => 'Subscription Plans';

  @override
  String get servicePrices => 'Service Prices';

  @override
  String get whyRousto => 'Why Rousto';

  @override
  String get aiScan => 'Photo Scan';

  @override
  String get artificialIntelligence => 'Artificial Intelligence';

  @override
  String get aiScanDescription =>
      'Take a photo of the issue and get a preliminary diagnosis and suggested service';

  @override
  String get scanType => 'Scan Type';

  @override
  String get noImageSelected => 'No image selected yet';

  @override
  String get chooseImage => 'Choose Image';

  @override
  String get analyzing => 'Analyzing...';

  @override
  String get analyzeImage => 'Analyze Image';

  @override
  String get scanResults => 'Scan Results';

  @override
  String get analysisComplete => 'Analysis complete';

  @override
  String estimatedAccuracy(int percent) {
    return 'Estimated accuracy $percent%';
  }

  @override
  String severity(String level) {
    return 'Severity $level';
  }

  @override
  String get severityHigh => 'High';

  @override
  String get severityLow => 'Low';

  @override
  String get severityMedium => 'Medium';

  @override
  String get suggestedService => 'Suggested Service';

  @override
  String bookService(String serviceName) {
    return 'Book $serviceName';
  }

  @override
  String get notifications => 'Notifications';

  @override
  String get markAllRead => 'Mark all read';

  @override
  String unreadCount(int count) {
    return '$count unread';
  }

  @override
  String get noNotifications => 'No notifications';

  @override
  String get notificationPreferences => 'Notification Preferences';

  @override
  String get inApp => 'In-app';

  @override
  String get push => 'Push';

  @override
  String get savePreferences => 'Save preferences';

  @override
  String get preferencesSaved => 'Preferences saved';

  @override
  String get onboardingTitle => 'Smart care for your car';

  @override
  String get onboardingSubtitle =>
      'Book maintenance service in seconds and track it live from your phone with certified technicians.';

  @override
  String get getStarted => 'Get Started';

  @override
  String get haveAccount => 'Already have an account? ';

  @override
  String get settings => 'Settings';

  @override
  String get settingsSubtitle => 'Notifications and language';

  @override
  String get myVehicles => 'My Vehicles';

  @override
  String vehicleCount(int count) {
    return '$count vehicle(s)';
  }

  @override
  String get orderHistory => 'Order History';

  @override
  String get inventory => 'Inventory';

  @override
  String previousServicesCount(int count) {
    return '$count previous service(s)';
  }

  @override
  String get paymentMethods => 'Payment Methods';

  @override
  String get paymentMethodsSubtitle => 'Mada, Apple Pay';

  @override
  String get addresses => 'Addresses';

  @override
  String get addressesSubtitle => 'Home, Work';

  @override
  String get rewards => 'Rewards';

  @override
  String loyaltyPointsAvailable(int points) {
    return '$points points available';
  }

  @override
  String get supportAndSafety => 'Support & Safety';

  @override
  String get supportSubtitle => 'Support tickets and FAQ';

  @override
  String get serviceStat => 'service';

  @override
  String get servicesStat => 'services';

  @override
  String get vehicleStat => 'vehicle';

  @override
  String get vehiclesStat => 'vehicles';

  @override
  String get pointsStat => 'points';

  @override
  String get savingsStat => 'saved';

  @override
  String membership(String plan) {
    return 'Membership $plan';
  }

  @override
  String membershipDiscount(int percent) {
    return ' · $percent% discount';
  }

  @override
  String get language => 'Language';

  @override
  String get arabic => 'Arabic';

  @override
  String get english => 'English';

  @override
  String get legal => 'Legal';

  @override
  String get privacyPolicy => 'Privacy Policy';

  @override
  String get termsOfService => 'Terms of Service';

  @override
  String get warrantyPolicy => 'Warranty Policy';

  @override
  String get connectionError => 'Connection error';

  @override
  String connectionErrorWithCode(int code) {
    return 'Connection error ($code)';
  }

  @override
  String get towingRequest => 'Towing Request';

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
  String get unknownInitial => '?';
}
