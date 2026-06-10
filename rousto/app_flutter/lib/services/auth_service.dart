import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import 'auth_storage.dart';

class AuthService {
  AuthService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Uri _uri(String path) =>
      Uri.parse('${AppConfig.apiBaseUrl}${AppConfig.apiPrefix}$path');

  Future<String> sendOtp(String phone) async {
    final res = await _client.post(
      _uri('/auth/otp/send'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone': phone}),
    );
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      final err = body['error'] as Map<String, dynamic>?;
      throw Exception(err?['message'] ?? 'فشل إرسال الرمز');
    }
    final meta = body['meta'] as Map<String, dynamic>?;
    return meta?['dev_otp'] as String? ?? '';
  }

  Future<void> verifyOtp({
    required String phone,
    required String code,
    String? requestId,
  }) async {
    final res = await _client.post(
      _uri('/auth/otp/verify'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'phone': phone,
        'code': code,
        if (requestId != null) 'request_id': requestId,
      }),
    );
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      final err = body['error'] as Map<String, dynamic>?;
      throw Exception(err?['message'] ?? 'فشل التحقق');
    }
    final data = body['data'] as Map<String, dynamic>;
    await AuthStorage.instance.saveTokens(
      access: data['access_token'] as String,
      refresh: data['refresh_token'] as String?,
    );
  }
}
