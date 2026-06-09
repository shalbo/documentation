import 'package:flutter/foundation.dart';

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
    ]);

    categories = results[0] as List<CategoryModel>;
    user = results[1] as UserModel;
    activeBooking = results[2] as BookingModel?;
    promotions = results[3] as List<PromotionModel>;
    loyaltyPoints = results[4] as int;
    usingMockData = !apiLive;
    loading = false;
    notifyListeners();
  }

  Future<void> refreshActiveBooking() async {
    activeBooking = await _repository.loadActiveBooking();
    notifyListeners();
  }

}
