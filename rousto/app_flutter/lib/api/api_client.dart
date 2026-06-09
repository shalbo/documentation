import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

class ApiClient {
  ApiClient({http.Client? client, String? baseUrl, String? userId})
      : _client = client ?? http.Client(),
        _baseUrl = baseUrl ?? AppConfig.apiBaseUrl,
        _userId = userId ?? AppConfig.defaultUserId;

  final http.Client _client;
  final String _baseUrl;
  final String _userId;

  Uri _uri(String path, [Map<String, String>? query]) {
    return Uri.parse('$_baseUrl${AppConfig.apiPrefix}$path')
        .replace(queryParameters: query);
  }

  Map<String, String> get _authHeaders => {'X-User-Id': _userId};

  Future<Map<String, dynamic>> _get(String path, {bool auth = false}) async {
    final headers = auth ? _authHeaders : <String, String>{};
    final response = await _client.get(_uri(path), headers: headers);
    _ensureSuccess(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> body, {
    bool auth = true,
  }) async {
    final headers = {
      'Content-Type': 'application/json',
      if (auth) ..._authHeaders,
    };
    final response = await _client.post(
      _uri(path),
      headers: headers,
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
        error?['message'] as String? ?? 'خطأ في الاتصال',
        statusCode: response.statusCode,
      );
    } catch (_) {
      throw ApiException('خطأ في الاتصال (${response.statusCode})',
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
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  const ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}
