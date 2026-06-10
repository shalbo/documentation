import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LocaleState extends ChangeNotifier {
  static const _prefKey = 'app_locale';

  /// Current language code used by [ApiClient] when no explicit locale is passed.
  static String languageCode = 'ar';

  Locale? _locale;

  Locale? get locale => _locale;

  bool get isRtl => (_locale ?? const Locale('ar')).languageCode == 'ar';

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final code = prefs.getString(_prefKey);
    if (code != null && (code == 'ar' || code == 'en')) {
      _locale = Locale(code);
      languageCode = code;
    } else {
      _locale = const Locale('ar');
      languageCode = 'ar';
    }
    notifyListeners();
  }

  Future<void> setLocale(Locale locale) async {
    _locale = locale;
    languageCode = locale.languageCode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefKey, locale.languageCode);
    notifyListeners();
  }
}
