import 'package:flutter/foundation.dart';

import '../currency.dart';
import '../data/app_repository.dart';
import '../data/models.dart';
import '../services/fitment_storage.dart';
import '../services/push_notifications.dart';

class AppState extends ChangeNotifier {
  AppState({AppRepository? repository})
      : _repository = repository ?? AppRepository();

  final AppRepository _repository;

  bool loading = true;
  bool usingMockData = false;

  UserModel? user;
  MarketplaceHomeModel? marketplace;
  BookingModel? activeBooking;
  int loyaltyPoints = 0;
  List<MembershipPlanModel> membershipPlans = [];
  List<ServicePackageModel> servicePackages = [];
  List<LoyaltyRewardModel> loyaltyRewards = [];
  MonetizationSummary? monetization;
  FitmentSelection? fitment;

  // Legacy service catalog — loaded lazily for booking flows only
  List<CategoryModel> serviceCategories = [];

  int _partCategoryIndex = 0;
  int get partCategoryIndex => _partCategoryIndex;

  List<PartCategoryModel> get partCategories => marketplace?.categories ?? [];

  List<PartListingModel> get visibleParts {
    final parts = marketplace?.featuredParts ?? [];
    if (partCategories.isEmpty) return parts;
    final idx = _partCategoryIndex.clamp(0, partCategories.length - 1);
    final slug = partCategories[idx].slug;
    return parts.where((p) => p.categorySlug == slug).toList();
  }

  List<MarketplaceVendorModel> get featuredVendors =>
      marketplace?.featuredVendors ?? [];

  List<PromotionModel> get promotions => marketplace?.promotions ?? [];

  void selectPartCategory(int index) {
    _partCategoryIndex = index;
    notifyListeners();
  }

  Future<void> setFitment(FitmentSelection? selection) async {
    fitment = selection;
    if (selection != null) {
      await FitmentStorage.instance.save(selection);
    } else {
      await FitmentStorage.instance.clear();
    }
    await reloadMarketplace();
  }

  Future<void> reloadMarketplace() async {
    marketplace = await _repository.loadMarketplaceHome(
      carYearId: fitment?.carYearId,
    );
    notifyListeners();
  }

  Future<void> load() async {
    loading = true;
    notifyListeners();

    fitment = await FitmentStorage.instance.load();
    final apiLive = await _repository.isApiAvailable();
    final results = await Future.wait([
      _repository.loadMarketplaceHome(carYearId: fitment?.carYearId),
      _repository.loadUser(),
      _repository.loadActiveBooking(),
      _repository.loadLoyaltyBalance(),
      _repository.loadMembershipPlans(),
      _repository.loadServicePackages(),
      _repository.loadLoyaltyRewards(),
      _repository.loadMonetizationSummary(),
    ]);

    marketplace = results[0] as MarketplaceHomeModel;
    user = results[1] as UserModel;
    activeBooking = results[2] as BookingModel?;
    loyaltyPoints = results[3] as int;
    membershipPlans = results[4] as List<MembershipPlanModel>;
    servicePackages = results[5] as List<ServicePackageModel>;
    loyaltyRewards = results[6] as List<LoyaltyRewardModel>;
    monetization = results[7] as MonetizationSummary;
    usingMockData = !apiLive;
    loading = false;
    notifyListeners();
    await PushNotifications.instance.registerWithBackend(_repository.api);
  }

  Future<void> ensureServiceCatalog() async {
    if (serviceCategories.isNotEmpty) return;
    serviceCategories = await _repository.loadCategories();
    notifyListeners();
  }

  Future<void> refreshActiveBooking() async {
    activeBooking = await _repository.loadActiveBooking();
    notifyListeners();
  }

  Future<bool> subscribeToPlan(String planSlug) async {
    final ok = await _repository.subscribePlan(planSlug);
    if (ok) monetization = await _repository.loadMonetizationSummary();
    notifyListeners();
    return ok;
  }

  Future<String?> redeemReward(String rewardSlug) async {
    final result = await _repository.redeemReward(rewardSlug);
    if (result.ok) {
      loyaltyPoints = result.balance;
      notifyListeners();
      return 'تم استبدال ${formatAmount(result.discount)} خصم';
    }
    return null;
  }
}
