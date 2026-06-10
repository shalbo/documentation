import 'package:shared_preferences/shared_preferences.dart';

import '../config/app_config.dart';

class AuthStorage {
  AuthStorage._();
  static final AuthStorage instance = AuthStorage._();

  static const _accessKey = 'rousto_access_token';
  static const _refreshKey = 'rousto_refresh_token';

  String? _accessToken;
  String? _refreshToken;

  String? get accessToken => _accessToken;
  String? get refreshToken => _refreshToken;
  bool get isLoggedIn => (_accessToken ?? '').isNotEmpty;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString(_accessKey);
    _refreshToken = prefs.getString(_refreshKey);
    if ((_accessToken ?? '').isEmpty && AppConfig.accessToken.isNotEmpty) {
      _accessToken = AppConfig.accessToken;
    }
  }

  Future<void> saveTokens({
    required String access,
    String? refresh,
  }) async {
    _accessToken = access;
    _refreshToken = refresh;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, access);
    if (refresh != null) {
      await prefs.setString(_refreshKey, refresh);
    }
  }

  Future<void> clear() async {
    _accessToken = null;
    _refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessKey);
    await prefs.remove(_refreshKey);
  }
}
