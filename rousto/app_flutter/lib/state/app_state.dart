import 'package:flutter/foundation.dart';

import '../currency.dart';
import '../data/app_repository.dart';
import '../data/models.dart';

class AppState extends ChangeNotifier {
  AppState({AppRepository? repository})
      : _repository = repository ?? AppRepository();

  final AppRepository _repository;

  bool loading = true;
  bool usingMockData = false;

  UserModel? user;
  List<CategoryModel> categories = [];
  BookingModel? activeBooking;
  List<PromotionModel> promotions = [];
  int loyaltyPoints = 0;
  List<MembershipPlanModel> membershipPlans = [];
  List<ServicePackageModel> servicePackages = [];
  List<LoyaltyRewardModel> loyaltyRewards = [];
  MonetizationSummary? monetization;

  List<ServiceModel> get currentServices {
    if (categories.isEmpty) return [];
    final index = _categoryIndex.clamp(0, categories.length - 1);
    return categories[index].services;
  }

  int _categoryIndex = 0;
  int get categoryIndex => _categoryIndex;

  void selectCategory(int index) {
    _categoryIndex = index;
    notifyListeners();
  }

  Future<void> load() async {
    loading = true;
    notifyListeners();

    final apiLive = await _repository.isApiAvailable();
    final results = await Future.wait([
      _repository.loadCategories(),
      _repository.loadUser(),
      _repository.loadActiveBooking(),
      _repository.loadPromotions(),
      _repository.loadLoyaltyBalance(),
      _repository.loadMembershipPlans(),
      _repository.loadServicePackages(),
      _repository.loadLoyaltyRewards(),
      _repository.loadMonetizationSummary(),
    ]);

    categories = results[0] as List<CategoryModel>;
    user = results[1] as UserModel;
    activeBooking = results[2] as BookingModel?;
    promotions = results[3] as List<PromotionModel>;
    loyaltyPoints = results[4] as int;
    membershipPlans = results[5] as List<MembershipPlanModel>;
    servicePackages = results[6] as List<ServicePackageModel>;
    loyaltyRewards = results[7] as List<LoyaltyRewardModel>;
    monetization = results[8] as MonetizationSummary;
    usingMockData = !apiLive;
    loading = false;
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
