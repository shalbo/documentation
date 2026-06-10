import '../../../../core/network/api_client.dart';

/// Vehicle fitment (make / model / year) for parts compatibility.
class FitmentRepository {
  FitmentRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<List<Map<String, dynamic>>> getMakes() async {
    final list = await _api.getFitmentMakes();
    return list.cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getModels(String makeId) async {
    final list = await _api.getFitmentModels(makeId);
    return list.cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getYears(String modelId) async {
    final list = await _api.getFitmentYears(modelId);
    return list.cast<Map<String, dynamic>>();
  }
}
