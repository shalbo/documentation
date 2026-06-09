import 'package:flutter/foundation.dart';

/// Firebase Cloud Messaging stub — enable with firebase_messaging in production.
class PushNotifications {
  PushNotifications._();
  static final PushNotifications instance = PushNotifications._();

  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;
    if (kReleaseMode) {
      // await Firebase.initializeApp();
      // await FirebaseMessaging.instance.requestPermission();
      // FirebaseMessaging.onBackgroundMessage(_bgHandler);
      debugPrint('PushNotifications: wire firebase_messaging for production');
    }
  }

  Future<String?> getToken() async => null;
}
