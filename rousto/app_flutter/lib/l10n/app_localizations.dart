import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('en')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Rousto'**
  String get appTitle;

  /// No description provided for @login.
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get login;

  /// No description provided for @phoneNumber.
  ///
  /// In en, this message translates to:
  /// **'Phone Number'**
  String get phoneNumber;

  /// No description provided for @verificationCode.
  ///
  /// In en, this message translates to:
  /// **'Verification Code'**
  String get verificationCode;

  /// No description provided for @devOtpHelper.
  ///
  /// In en, this message translates to:
  /// **'Development mode: {otp}'**
  String devOtpHelper(String otp);

  /// No description provided for @codeSent.
  ///
  /// In en, this message translates to:
  /// **'Code sent'**
  String get codeSent;

  /// No description provided for @confirmLogin.
  ///
  /// In en, this message translates to:
  /// **'Confirm Login'**
  String get confirmLogin;

  /// No description provided for @sendCode.
  ///
  /// In en, this message translates to:
  /// **'Send Code'**
  String get sendCode;

  /// No description provided for @navHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get navHome;

  /// No description provided for @navOrders.
  ///
  /// In en, this message translates to:
  /// **'My Requests'**
  String get navOrders;

  /// No description provided for @navOffers.
  ///
  /// In en, this message translates to:
  /// **'Offers'**
  String get navOffers;

  /// No description provided for @navAccount.
  ///
  /// In en, this message translates to:
  /// **'Account'**
  String get navAccount;

  /// No description provided for @welcomeBack.
  ///
  /// In en, this message translates to:
  /// **'Welcome back 👋'**
  String get welcomeBack;

  /// No description provided for @guest.
  ///
  /// In en, this message translates to:
  /// **'Guest'**
  String get guest;

  /// No description provided for @searchService.
  ///
  /// In en, this message translates to:
  /// **'Search for a service…'**
  String get searchService;

  /// No description provided for @activeService.
  ///
  /// In en, this message translates to:
  /// **'Active Service'**
  String get activeService;

  /// No description provided for @service.
  ///
  /// In en, this message translates to:
  /// **'Service'**
  String get service;

  /// No description provided for @popularServices.
  ///
  /// In en, this message translates to:
  /// **'Popular Services'**
  String get popularServices;

  /// No description provided for @viewAll.
  ///
  /// In en, this message translates to:
  /// **'View All'**
  String get viewAll;

  /// No description provided for @pricingPlans.
  ///
  /// In en, this message translates to:
  /// **'Pricing & Plans'**
  String get pricingPlans;

  /// No description provided for @pricingPlansSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Individual · Family · Business — in Dinar'**
  String get pricingPlansSubtitle;

  /// No description provided for @photoScan.
  ///
  /// In en, this message translates to:
  /// **'Photo Scan'**
  String get photoScan;

  /// No description provided for @photoScanSubtitle.
  ///
  /// In en, this message translates to:
  /// **'AI preliminary diagnosis'**
  String get photoScanSubtitle;

  /// No description provided for @firstBookingDiscount.
  ///
  /// In en, this message translates to:
  /// **'First booking discount'**
  String get firstBookingDiscount;

  /// No description provided for @useCode.
  ///
  /// In en, this message translates to:
  /// **'Use code {code}'**
  String useCode(String code);

  /// No description provided for @promoPercent.
  ///
  /// In en, this message translates to:
  /// **'25%'**
  String get promoPercent;

  /// No description provided for @demoMode.
  ///
  /// In en, this message translates to:
  /// **'Demo mode'**
  String get demoMode;

  /// No description provided for @noActiveBooking.
  ///
  /// In en, this message translates to:
  /// **'No active booking'**
  String get noActiveBooking;

  /// No description provided for @refresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh'**
  String get refresh;

  /// No description provided for @trackService.
  ///
  /// In en, this message translates to:
  /// **'Tracking'**
  String get trackService;

  /// No description provided for @messageTechnician.
  ///
  /// In en, this message translates to:
  /// **'Message Technician'**
  String get messageTechnician;

  /// No description provided for @distanceKm.
  ///
  /// In en, this message translates to:
  /// **'Distance {distance} km'**
  String distanceKm(String distance);

  /// No description provided for @arrivesInMinutes.
  ///
  /// In en, this message translates to:
  /// **'Arrives in {minutes} min'**
  String arrivesInMinutes(int minutes);

  /// No description provided for @distanceWithEta.
  ///
  /// In en, this message translates to:
  /// **'Distance {distance} km · Arrives in {minutes} min'**
  String distanceWithEta(String distance, int minutes);

  /// No description provided for @bookingStatusLine.
  ///
  /// In en, this message translates to:
  /// **'{serviceName} · {status}'**
  String bookingStatusLine(String serviceName, String status);

  /// No description provided for @offersAndSubscriptions.
  ///
  /// In en, this message translates to:
  /// **'Offers & Subscriptions'**
  String get offersAndSubscriptions;

  /// No description provided for @fullPricingPage.
  ///
  /// In en, this message translates to:
  /// **'Full Pricing Page'**
  String get fullPricingPage;

  /// No description provided for @fullPricingSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Plans · Packages · Service Prices'**
  String get fullPricingSubtitle;

  /// No description provided for @yourPointsBalance.
  ///
  /// In en, this message translates to:
  /// **'Your Points Balance'**
  String get yourPointsBalance;

  /// No description provided for @points.
  ///
  /// In en, this message translates to:
  /// **'points'**
  String get points;

  /// No description provided for @point.
  ///
  /// In en, this message translates to:
  /// **'point'**
  String get point;

  /// No description provided for @pointsDiscountInfo.
  ///
  /// In en, this message translates to:
  /// **'Enough for {discount} off — 100 points = {amount}'**
  String pointsDiscountInfo(String discount, String amount);

  /// No description provided for @membershipPlans.
  ///
  /// In en, this message translates to:
  /// **'Membership Plans'**
  String get membershipPlans;

  /// No description provided for @maintenancePackages.
  ///
  /// In en, this message translates to:
  /// **'Maintenance Packages'**
  String get maintenancePackages;

  /// No description provided for @redeemPoints.
  ///
  /// In en, this message translates to:
  /// **'Redeem Points'**
  String get redeemPoints;

  /// No description provided for @exclusiveOffers.
  ///
  /// In en, this message translates to:
  /// **'Exclusive Offers'**
  String get exclusiveOffers;

  /// No description provided for @free.
  ///
  /// In en, this message translates to:
  /// **'Free'**
  String get free;

  /// No description provided for @subscribeNow.
  ///
  /// In en, this message translates to:
  /// **'Subscribe Now'**
  String get subscribeNow;

  /// No description provided for @yourCurrentPlan.
  ///
  /// In en, this message translates to:
  /// **'Your Current Plan'**
  String get yourCurrentPlan;

  /// No description provided for @subscribedToPlan.
  ///
  /// In en, this message translates to:
  /// **'Subscribed to {planName} plan'**
  String subscribedToPlan(String planName);

  /// No description provided for @subscribeFailed.
  ///
  /// In en, this message translates to:
  /// **'Subscription failed — demo mode'**
  String get subscribeFailed;

  /// No description provided for @redeem.
  ///
  /// In en, this message translates to:
  /// **'Redeem'**
  String get redeem;

  /// No description provided for @redeemFailed.
  ///
  /// In en, this message translates to:
  /// **'Redemption failed'**
  String get redeemFailed;

  /// No description provided for @visitsSave.
  ///
  /// In en, this message translates to:
  /// **'{visits} visits · Save {savings}'**
  String visitsSave(int visits, String savings);

  /// No description provided for @pointsCost.
  ///
  /// In en, this message translates to:
  /// **'{points} points'**
  String pointsCost(int points);

  /// No description provided for @confirmBooking.
  ///
  /// In en, this message translates to:
  /// **'Confirm Booking'**
  String get confirmBooking;

  /// No description provided for @yourVehicle.
  ///
  /// In en, this message translates to:
  /// **'Your Vehicle'**
  String get yourVehicle;

  /// No description provided for @appointment.
  ///
  /// In en, this message translates to:
  /// **'Appointment'**
  String get appointment;

  /// No description provided for @slotSaturday.
  ///
  /// In en, this message translates to:
  /// **'Saturday'**
  String get slotSaturday;

  /// No description provided for @slotSunday9am.
  ///
  /// In en, this message translates to:
  /// **'Sunday 9 AM'**
  String get slotSunday9am;

  /// No description provided for @slotMonday.
  ///
  /// In en, this message translates to:
  /// **'Monday'**
  String get slotMonday;

  /// No description provided for @slotTuesday.
  ///
  /// In en, this message translates to:
  /// **'Tuesday'**
  String get slotTuesday;

  /// No description provided for @location.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get location;

  /// No description provided for @paymentMethod.
  ///
  /// In en, this message translates to:
  /// **'Payment Method'**
  String get paymentMethod;

  /// No description provided for @wallet.
  ///
  /// In en, this message translates to:
  /// **'Wallet'**
  String get wallet;

  /// No description provided for @virtualCard.
  ///
  /// In en, this message translates to:
  /// **'Virtual card'**
  String get virtualCard;

  /// No description provided for @serviceSummary.
  ///
  /// In en, this message translates to:
  /// **'Service'**
  String get serviceSummary;

  /// No description provided for @discountLabel.
  ///
  /// In en, this message translates to:
  /// **'Discount (ROUSTO)'**
  String get discountLabel;

  /// No description provided for @total.
  ///
  /// In en, this message translates to:
  /// **'Total'**
  String get total;

  /// No description provided for @paymentSplit.
  ///
  /// In en, this message translates to:
  /// **'Payment Split'**
  String get paymentSplit;

  /// No description provided for @confirmAndPay.
  ///
  /// In en, this message translates to:
  /// **'Confirm & Pay {amount}'**
  String confirmAndPay(String amount);

  /// No description provided for @bookingConfirmed.
  ///
  /// In en, this message translates to:
  /// **'Booking confirmed!'**
  String get bookingConfirmed;

  /// No description provided for @bookingSavedLocally.
  ///
  /// In en, this message translates to:
  /// **'Booking saved locally'**
  String get bookingSavedLocally;

  /// No description provided for @bookingConfirmedDetail.
  ///
  /// In en, this message translates to:
  /// **'The Rousto team will contact you to confirm details.'**
  String get bookingConfirmedDetail;

  /// No description provided for @bookingSavedDetail.
  ///
  /// In en, this message translates to:
  /// **'Could not reach server — saved in demo mode.'**
  String get bookingSavedDetail;

  /// No description provided for @ok.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// No description provided for @noServicesAvailable.
  ///
  /// In en, this message translates to:
  /// **'No services available'**
  String get noServicesAvailable;

  /// No description provided for @pricing.
  ///
  /// In en, this message translates to:
  /// **'Pricing'**
  String get pricing;

  /// No description provided for @plansForEveryNeed.
  ///
  /// In en, this message translates to:
  /// **'Plans for every need'**
  String get plansForEveryNeed;

  /// No description provided for @transparentPricing.
  ///
  /// In en, this message translates to:
  /// **'Transparent pricing in Dinar — updated from server'**
  String get transparentPricing;

  /// No description provided for @subscriptionPlans.
  ///
  /// In en, this message translates to:
  /// **'Subscription Plans'**
  String get subscriptionPlans;

  /// No description provided for @servicePrices.
  ///
  /// In en, this message translates to:
  /// **'Service Prices'**
  String get servicePrices;

  /// No description provided for @whyRousto.
  ///
  /// In en, this message translates to:
  /// **'Why Rousto'**
  String get whyRousto;

  /// No description provided for @aiScan.
  ///
  /// In en, this message translates to:
  /// **'Photo Scan'**
  String get aiScan;

  /// No description provided for @artificialIntelligence.
  ///
  /// In en, this message translates to:
  /// **'Artificial Intelligence'**
  String get artificialIntelligence;

  /// No description provided for @aiScanDescription.
  ///
  /// In en, this message translates to:
  /// **'Take a photo of the issue and get a preliminary diagnosis and suggested service'**
  String get aiScanDescription;

  /// No description provided for @scanType.
  ///
  /// In en, this message translates to:
  /// **'Scan Type'**
  String get scanType;

  /// No description provided for @noImageSelected.
  ///
  /// In en, this message translates to:
  /// **'No image selected yet'**
  String get noImageSelected;

  /// No description provided for @chooseImage.
  ///
  /// In en, this message translates to:
  /// **'Choose Image'**
  String get chooseImage;

  /// No description provided for @analyzing.
  ///
  /// In en, this message translates to:
  /// **'Analyzing...'**
  String get analyzing;

  /// No description provided for @analyzeImage.
  ///
  /// In en, this message translates to:
  /// **'Analyze Image'**
  String get analyzeImage;

  /// No description provided for @scanResults.
  ///
  /// In en, this message translates to:
  /// **'Scan Results'**
  String get scanResults;

  /// No description provided for @analysisComplete.
  ///
  /// In en, this message translates to:
  /// **'Analysis complete'**
  String get analysisComplete;

  /// No description provided for @estimatedAccuracy.
  ///
  /// In en, this message translates to:
  /// **'Estimated accuracy {percent}%'**
  String estimatedAccuracy(int percent);

  /// No description provided for @severity.
  ///
  /// In en, this message translates to:
  /// **'Severity {level}'**
  String severity(String level);

  /// No description provided for @severityHigh.
  ///
  /// In en, this message translates to:
  /// **'High'**
  String get severityHigh;

  /// No description provided for @severityLow.
  ///
  /// In en, this message translates to:
  /// **'Low'**
  String get severityLow;

  /// No description provided for @severityMedium.
  ///
  /// In en, this message translates to:
  /// **'Medium'**
  String get severityMedium;

  /// No description provided for @suggestedService.
  ///
  /// In en, this message translates to:
  /// **'Suggested Service'**
  String get suggestedService;

  /// No description provided for @bookService.
  ///
  /// In en, this message translates to:
  /// **'Book {serviceName}'**
  String bookService(String serviceName);

  /// No description provided for @notifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notifications;

  /// No description provided for @markAllRead.
  ///
  /// In en, this message translates to:
  /// **'Mark all read'**
  String get markAllRead;

  /// No description provided for @unreadCount.
  ///
  /// In en, this message translates to:
  /// **'{count} unread'**
  String unreadCount(int count);

  /// No description provided for @noNotifications.
  ///
  /// In en, this message translates to:
  /// **'No notifications'**
  String get noNotifications;

  /// No description provided for @notificationPreferences.
  ///
  /// In en, this message translates to:
  /// **'Notification Preferences'**
  String get notificationPreferences;

  /// No description provided for @inApp.
  ///
  /// In en, this message translates to:
  /// **'In-app'**
  String get inApp;

  /// No description provided for @push.
  ///
  /// In en, this message translates to:
  /// **'Push'**
  String get push;

  /// No description provided for @savePreferences.
  ///
  /// In en, this message translates to:
  /// **'Save preferences'**
  String get savePreferences;

  /// No description provided for @preferencesSaved.
  ///
  /// In en, this message translates to:
  /// **'Preferences saved'**
  String get preferencesSaved;

  /// No description provided for @onboardingTitle.
  ///
  /// In en, this message translates to:
  /// **'Smart care for your car'**
  String get onboardingTitle;

  /// No description provided for @onboardingSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Book maintenance service in seconds and track it live from your phone with certified technicians.'**
  String get onboardingSubtitle;

  /// No description provided for @getStarted.
  ///
  /// In en, this message translates to:
  /// **'Get Started'**
  String get getStarted;

  /// No description provided for @haveAccount.
  ///
  /// In en, this message translates to:
  /// **'Already have an account? '**
  String get haveAccount;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @settingsSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Notifications and language'**
  String get settingsSubtitle;

  /// No description provided for @myVehicles.
  ///
  /// In en, this message translates to:
  /// **'My Vehicles'**
  String get myVehicles;

  /// No description provided for @vehicleCount.
  ///
  /// In en, this message translates to:
  /// **'{count} vehicle(s)'**
  String vehicleCount(int count);

  /// No description provided for @orderHistory.
  ///
  /// In en, this message translates to:
  /// **'Order History'**
  String get orderHistory;

  /// No description provided for @inventory.
  ///
  /// In en, this message translates to:
  /// **'Inventory'**
  String get inventory;

  /// No description provided for @previousServicesCount.
  ///
  /// In en, this message translates to:
  /// **'{count} previous service(s)'**
  String previousServicesCount(int count);

  /// No description provided for @paymentMethods.
  ///
  /// In en, this message translates to:
  /// **'Payment Methods'**
  String get paymentMethods;

  /// No description provided for @paymentMethodsSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Mada, Apple Pay'**
  String get paymentMethodsSubtitle;

  /// No description provided for @addresses.
  ///
  /// In en, this message translates to:
  /// **'Addresses'**
  String get addresses;

  /// No description provided for @addressesSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Home, Work'**
  String get addressesSubtitle;

  /// No description provided for @rewards.
  ///
  /// In en, this message translates to:
  /// **'Rewards'**
  String get rewards;

  /// No description provided for @loyaltyPointsAvailable.
  ///
  /// In en, this message translates to:
  /// **'{points} points available'**
  String loyaltyPointsAvailable(int points);

  /// No description provided for @supportAndSafety.
  ///
  /// In en, this message translates to:
  /// **'Support & Safety'**
  String get supportAndSafety;

  /// No description provided for @supportSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Support tickets and FAQ'**
  String get supportSubtitle;

  /// No description provided for @serviceStat.
  ///
  /// In en, this message translates to:
  /// **'service'**
  String get serviceStat;

  /// No description provided for @servicesStat.
  ///
  /// In en, this message translates to:
  /// **'services'**
  String get servicesStat;

  /// No description provided for @vehicleStat.
  ///
  /// In en, this message translates to:
  /// **'vehicle'**
  String get vehicleStat;

  /// No description provided for @vehiclesStat.
  ///
  /// In en, this message translates to:
  /// **'vehicles'**
  String get vehiclesStat;

  /// No description provided for @pointsStat.
  ///
  /// In en, this message translates to:
  /// **'points'**
  String get pointsStat;

  /// No description provided for @savingsStat.
  ///
  /// In en, this message translates to:
  /// **'saved'**
  String get savingsStat;

  /// No description provided for @membership.
  ///
  /// In en, this message translates to:
  /// **'Membership {plan}'**
  String membership(String plan);

  /// No description provided for @membershipDiscount.
  ///
  /// In en, this message translates to:
  /// **' · {percent}% discount'**
  String membershipDiscount(int percent);

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @arabic.
  ///
  /// In en, this message translates to:
  /// **'Arabic'**
  String get arabic;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @legal.
  ///
  /// In en, this message translates to:
  /// **'Legal'**
  String get legal;

  /// No description provided for @privacyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy;

  /// No description provided for @termsOfService.
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfService;

  /// No description provided for @warrantyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Warranty Policy'**
  String get warrantyPolicy;

  /// No description provided for @connectionError.
  ///
  /// In en, this message translates to:
  /// **'Connection error'**
  String get connectionError;

  /// No description provided for @connectionErrorWithCode.
  ///
  /// In en, this message translates to:
  /// **'Connection error ({code})'**
  String connectionErrorWithCode(int code);

  /// No description provided for @towingRequest.
  ///
  /// In en, this message translates to:
  /// **'Towing Request'**
  String get towingRequest;

  /// No description provided for @privacyContent.
  ///
  /// In en, this message translates to:
  /// **'Rousto Privacy Policy\n\nWe collect your phone number, vehicle information, and service history to provide automotive care services. Your data is encrypted in transit and stored securely. We do not sell personal data to third parties. Location data is used only during active service tracking. You may request data deletion by contacting support.\n\nContact: privacy@rousto.com'**
  String get privacyContent;

  /// No description provided for @termsContent.
  ///
  /// In en, this message translates to:
  /// **'Rousto Terms of Service\n\nBy using Rousto you agree to book services at listed prices, provide accurate vehicle information, and allow technicians access to perform requested work. Cancellations within 2 hours of appointment may incur a fee. Rousto acts as a platform connecting you with certified automotive service providers. Disputes are handled through in-app support.\n\nContact: legal@rousto.com'**
  String get termsContent;

  /// No description provided for @warrantyContent.
  ///
  /// In en, this message translates to:
  /// **'Rousto Service Warranty\n\nServices booked through Rousto include a 7-day workmanship warranty on maintenance and repair work performed by certified technicians. Parts warranty follows manufacturer terms. Towing and emergency services are covered for the duration of the service session. To file a warranty claim, open a support ticket in the app with your booking reference.\n\nContact: warranty@rousto.com'**
  String get warrantyContent;

  /// No description provided for @privacyContentAr.
  ///
  /// In en, this message translates to:
  /// **'سياسة الخصوصية — روستو\n\nنجمع رقم جوالك ومعلومات مركبتك وسجل الخدمات لتقديم خدمات العناية بالسيارات. بياناتك مشفّرة أثناء النقل ومخزّنة بأمان. لا نبيع البيانات الشخصية لأطراف ثالثة. بيانات الموقع تُستخدم فقط أثناء تتبّع الخدمة النشطة. يمكنك طلب حذف البيانات عبر الدعم.\n\nالتواصل: privacy@rousto.com'**
  String get privacyContentAr;

  /// No description provided for @termsContentAr.
  ///
  /// In en, this message translates to:
  /// **'شروط الخدمة — روستو\n\nباستخدام روستو فإنك توافق على حجز الخدمات بالأسعار المعلنة وتقديم معلومات دقيقة عن مركبتك والسماح للفنيين بإنجاز العمل المطلوب. الإلغاء خلال ساعتين من الموعد قد يترتب عليه رسوم. روستو منصة تربطك بمقدّمي خدمات سيارات معتمدين. النزاعات تُعالج عبر دعم التطبيق.\n\nالتواصل: legal@rousto.com'**
  String get termsContentAr;

  /// No description provided for @warrantyContentAr.
  ///
  /// In en, this message translates to:
  /// **'ضمان الخدمة — روستو\n\nالخدمات المحجوزة عبر روستو تشمل ضمان إنجاز لمدة 7 أيام على أعمال الصيانة والإصلاح التي ينفّذها فنيون معتمدون. ضمان القطع يتبع شروط الشركة المصنّعة. السحب والخدمات الطارئة مغطاة طوال جلسة الخدمة. لرفع مطالبة ضمان، افتح تذكرة دعم في التطبيق مع رقم الحجز.\n\nالتواصل: warranty@rousto.com'**
  String get warrantyContentAr;

  /// No description provided for @unknownInitial.
  ///
  /// In en, this message translates to:
  /// **'?'**
  String get unknownInitial;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
