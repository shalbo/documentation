import '../../../../core/network/api_client.dart';

/// Spare parts search, categories, and marketplace.
class PartsRepository {
  PartsRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<Map<String, dynamic>> getMarketplaceHome({String? carYearId}) {
    return _api.getMarketplaceHome(carYearId: carYearId);
  }

  Future<({List<dynamic> data, Map<String, dynamic>? meta})> searchParts({
    String? query,
    String? category,
    String? categoryId,
    String? carYearId,
    String? oem,
    String? vin,
    String? condition,
    bool inStockOnly = false,
  }) {
    return _api.searchParts(
      query: query,
      category: category,
      categoryId: categoryId,
      carYearId: carYearId,
      oem: oem,
      vin: vin,
      condition: condition,
      inStockOnly: inStockOnly,
    );
  }

  Future<List<Map<String, dynamic>>> getCategoryRoots() async {
    final list = await _api.getCategoryRoots();
    return list.cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getCategoryChildren(String parentId) async {
    final list = await _api.getCategoryChildren(parentId);
    return list.cast<Map<String, dynamic>>();
  }

  Future<List<dynamic>> getCategoriesTree() {
    return _api.getCategoriesTree();
  }
}
