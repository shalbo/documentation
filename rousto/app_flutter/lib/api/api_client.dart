import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../services/auth_storage.dart';
import '../state/locale_state.dart';

class ApiClient {
  ApiClient({
    http.Client? client,
    String? baseUrl,
    String? userId,
    String? languageCode,
  })  : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl,
        _userId = userId ?? AppConfig.defaultUserId,
        _languageCode = languageCode ?? LocaleState.languageCode;

  final http.Client _client;
  final String _baseUrl;
  final String _userId;
  final String _languageCode;

  Uri _uri(String path, [Map<String, String>? query]) {
    return Uri.parse('$_baseUrl${AppConfig.apiPrefix}$path')
        .replace(queryParameters: query);
  }

  Map<String, String> get _authHeaders {
    final token = AuthStorage.instance.accessToken;
    if (token != null && token.isNotEmpty) {
      return {'Authorization': 'Bearer $token'};
    }
    if (AppConfig.useLegacyUserHeader) {
      return {'X-User-Id': _userId};
    }
    return {};
  }

  Map<String, String> _headers({bool auth = false, bool json = false}) {
    return {
      'Accept-Language': _languageCode,
      if (json) 'Content-Type': 'application/json',
      if (auth) ..._authHeaders,
    };
  }

  Future<Map<String, dynamic>> _get(String path, {bool auth = false}) async {
    final headers = _headers(auth: auth);
    final response = await _client.get(_uri(path), headers: headers);
    _ensureSuccess(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> body, {
    bool auth = true,
  }) async {
    final response = await _client.post(
      _uri(path),
      headers: _headers(auth: auth, json: true),
      body: jsonEncode(body),
    );
    _ensureSuccess(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  void _ensureSuccess(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) return;
    try {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      final error = body['error'] as Map<String, dynamic>?;
      throw ApiException(
        error?['message'] as String? ?? 'Connection error',
        statusCode: response.statusCode,
      );
    } catch (_) {
      throw ApiException('Connection error (${response.statusCode})',
          statusCode: response.statusCode);
    }
  }

  Future<bool> ping() async {
    try {
      await _get('/health');
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>> getMarketplaceHome({String? carYearId}) async {
    final query = carYearId != null ? {'car_year_id': carYearId} : null;
    final response = await _client.get(
      _uri('/marketplace/home', query),
      headers: _headers(),
    );
    _ensureSuccess(response);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return body['data'] as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getFitmentMakes() async {
    final body = await _get('/fitment/makes');
    return (body['data'] as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getFitmentModels(String makeId) async {
    final response = await _client.get(
      _uri('/fitment/models', {'make_id': makeId}),
      headers: _headers(),
    );
    _ensureSuccess(response);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return (body['data'] as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getFitmentYears(String modelId) async {
    final response = await _client.get(
      _uri('/fitment/years', {'model_id': modelId}),
      headers: _headers(),
    );
    _ensureSuccess(response);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return (body['data'] as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getCategoryRoots() async {
    final body = await _get('/parts/categories/roots');
    return (body['data'] as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getCategoryChildren(String parentId) async {
    final response = await _client.get(
      _uri('/parts/categories/$parentId/children'),
      headers: _headers(),
    );
    _ensureSuccess(response);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return (body['data'] as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<({List<dynamic> data, Map<String, dynamic>? meta})> searchParts({
    String? query,
    String? category,
    String? categoryId,
    String? carYearId,
    String? oem,
    String? vin,
    String? condition,
    bool oemOnly = false,
    bool inStockOnly = false,
    int limit = 50,
  }) async {
    final params = <String, String>{
      if (query != null && query.isNotEmpty) 'q': query,
      if (category != null && category.isNotEmpty) 'category': category,
      if (categoryId != null && categoryId.isNotEmpty) 'category_id': categoryId,
      if (carYearId != null && carYearId.isNotEmpty) 'car_year_id': carYearId,
      if (oem != null && oem.isNotEmpty) 'oem': oem,
      if (vin != null && vin.isNotEmpty) 'vin': vin,
      if (condition != null && condition.isNotEmpty) 'condition': condition,
      if (oemOnly) 'oem_only': 'true',
      if (inStockOnly) 'in_stock_only': 'true',
      'limit': '$limit',
    };
    final hasFilter = params.containsKey('car_year_id') ||
        params.containsKey('category_id') ||
        params.containsKey('q') ||
        params.containsKey('category') ||
        params.containsKey('oem') ||
        params.containsKey('vin') ||
        params.containsKey('condition');
    if (!hasFilter) {
      throw ApiException('أدخل نص بحث أو فئة أو مركبة');
    }
    final response = await _client.get(
      _uri('/parts/search', params),
      headers: _headers(),
    );
    _ensureSuccess(response);
    final parsed = jsonDecode(response.body) as Map<String, dynamic>;
    return (
      data: parsed['data'] as List<dynamic>,
      meta: parsed['meta'] as Map<String, dynamic>?,
    );
  }

  Future<List<dynamic>> getPartCategories() async {
    final body = await _get('/parts/categories');
    return body['data'] as List<dynamic>;
  }

  Future<List<dynamic>> getCategoriesTree() async {
    final body = await _get('/categories/tree');
    return body['data'] as List<dynamic>;
  }

  Future<Map<String, dynamic>?> getMe() async {
    final body = await _get('/me', auth: true);
    return body['data'] as Map<String, dynamic>?;
  }

  Future<Map<String, dynamic>?> getActiveBooking() async {
    final body = await _get('/bookings/active', auth: true);
    return body['data'] as Map<String, dynamic>?;
  }

  Future<Map<String, dynamic>> getBookingTracking(String bookingId) async {
    final body = await _get('/bookings/$bookingId/tracking', auth: true);
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getBookingDeliveryMap(String bookingId) async {
    final body = await _get('/bookings/$bookingId/delivery-map', auth: true);
    return body['data'] as Map<String, dynamic>;
  }

  Future<List<dynamic>> getPromotions() async {
    final body = await _get('/promotions');
    return body['data'] as List<dynamic>;
  }

  Future<Map<String, dynamic>> getLoyalty() async {
    final body = await _get('/me/loyalty', auth: true);
    return body['data'] as Map<String, dynamic>;
  }

  Future<List<dynamic>> getVehicles() async {
    final body = await _get('/me/vehicles', auth: true);
    return body['data'] as List<dynamic>;
  }

  Future<List<dynamic>> getAddresses() async {
    final body = await _get('/me/addresses', auth: true);
    return body['data'] as List<dynamic>;
  }

  Future<List<dynamic>> getPaymentMethods() async {
    final body = await _get('/me/payment-methods', auth: true);
    return body['data'] as List<dynamic>;
  }

  Future<Map<String, dynamic>> validatePromotion(
    String code,
    double servicePrice,
  ) async {
    final body = await _post('/promotions/validate', {
      'code': code,
      'service_price_sar': servicePrice,
    });
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createBooking(Map<String, dynamic> payload) async {
    final body = await _post('/bookings', payload);
    return body['data'] as Map<String, dynamic>;
  }

  Future<List<dynamic>> getMembershipPlans() async {
    final body = await _get('/monetization/plans');
    return body['data'] as List<dynamic>;
  }

  Future<List<dynamic>> getServicePackages() async {
    final body = await _get('/monetization/packages');
    return body['data'] as List<dynamic>;
  }

  Future<List<dynamic>> getLoyaltyRewards() async {
    final body = await _get('/monetization/rewards');
    return body['data'] as List<dynamic>;
  }

  Future<Map<String, dynamic>> getMonetizationSummary() async {
    final body = await _get('/me/monetization', auth: true);
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> subscribeMembership(String planSlug) async {
    final body = await _post('/me/membership/subscribe', {
      'plan_slug': planSlug,
    });
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> redeemReward(String rewardSlug) async {
    final body = await _post('/me/loyalty/redeem', {
      'reward_slug': rewardSlug,
    });
    return body['data'] as Map<String, dynamic>;
  }

  Future<List<dynamic>> getScanTypes() async {
    final body = await _get('/scans/types');
    return body['data'] as List<dynamic>;
  }

  Future<Map<String, dynamic>> createScan({
    required String vehicleId,
    required String scanType,
    required List<int> imageBytes,
    required String filename,
  }) async {
    final request = http.MultipartRequest('POST', _uri('/scans'));
    request.headers.addAll(_headers(auth: true));
    request.fields['vehicle_id'] = vehicleId;
    request.fields['scan_type'] = scanType;
    request.files.add(
      http.MultipartFile.fromBytes('images', imageBytes, filename: filename),
    );
    final streamed = await _client.send(request);
    final response = await http.Response.fromStream(streamed);
    _ensureSuccess(response);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getScan(String scanId) async {
    final body = await _get('/scans/$scanId', auth: true);
    return body['data'] as Map<String, dynamic>;
  }

  Future<List<dynamic>> getMyScans() async {
    final body = await _get('/me/scans', auth: true);
    return body['data'] as List<dynamic>;
  }

  Future<Map<String, dynamic>> previewPaymentSplit(double amountSar) async {
    final body = await _post('/payments/split/preview', {
      'amount_sar': amountSar,
    }, auth: false);
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getLandingPricing() async {
    final body = await _get('/landing/pricing');
    return body['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getLandingPage() async {
    final body = await _get('/landing/page');
    return body['data'] as Map<String, dynamic>;
  }

  Future<void> registerDevice({
    required String fcmToken,
    required String platform,
  }) async {
    await _post('/me/devices/register', {
      'fcm_token': fcmToken,
      'platform': platform,
    });
  }

  Future<List<Map<String, dynamic>>> getNotifications({
    bool unreadOnly = false,
    String? category,
  }) async {
    final query = <String, String>{};
    if (unreadOnly) query['unread_only'] = 'true';
    if (category != null) query['category'] = category;
    final response = await _client.get(
      _uri('/me/notifications', query.isEmpty ? null : query),
      headers: _headers(auth: true),
    );
    _ensureSuccess(response);
    final parsed = jsonDecode(response.body) as Map<String, dynamic>;
    final data = parsed['data'] as List<dynamic>;
    return data.cast<Map<String, dynamic>>();
  }

  Future<int> getNotificationUnreadCount() async {
    final body = await _get('/me/notifications/unread-count', auth: true);
    final data = body['data'] as Map<String, dynamic>;
    return data['count'] as int? ?? 0;
  }

  Future<void> markNotificationRead(String id) async {
    await _patch('/me/notifications/$id/read');
  }

  Future<void> markAllNotificationsRead() async {
    await _post('/me/notifications/read-all', {}, auth: true);
  }

  Future<List<Map<String, dynamic>>> getNotificationPreferences() async {
    final body = await _get('/me/notification-preferences', auth: true);
    final data = body['data'] as List<dynamic>;
    return data.cast<Map<String, dynamic>>();
  }

  Future<void> updateNotificationPreferences(
    List<Map<String, dynamic>> preferences,
  ) async {
    await _put('/me/notification-preferences', {
      'preferences': preferences,
    });
  }

  Future<Map<String, dynamic>> _put(
    String path,
    Map<String, dynamic> body, {
    bool auth = true,
  }) async {
    final response = await _client.put(
      _uri(path),
      headers: _headers(auth: auth, json: true),
      body: jsonEncode(body),
    );
    _ensureSuccess(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> _patch(
    String path, {
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    final response = await _client.patch(
      _uri(path),
      headers: _headers(auth: auth, json: true),
      body: body != null ? jsonEncode(body) : null,
    );
    _ensureSuccess(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  const ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}
