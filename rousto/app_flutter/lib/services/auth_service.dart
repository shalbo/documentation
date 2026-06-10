import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import 'auth_storage.dart';

class AuthService {
  AuthService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Uri _uri(String path) =>
      Uri.parse('${AppConfig.apiBaseUrl}${AppConfig.apiPrefix}$path');

  Future<void> login({
    required String phone,
    required String password,
  }) async {
    final res = await _client.post(
      _uri('/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone': phone, 'password': password}),
    );
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      final detail = body['detail'] as Map<String, dynamic>?;
      final err = body['error'] as Map<String, dynamic>?;
      throw Exception(
        detail?['message'] ?? err?['message'] ?? 'فشل تسجيل الدخول',
      );
    }
    final data = body['data'] as Map<String, dynamic>;
    await AuthStorage.instance.saveTokens(
      access: data['access_token'] as String,
      refresh: data['refresh_token'] as String?,
    );
  }
}
