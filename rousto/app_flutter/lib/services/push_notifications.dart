import 'dart:io' show Platform;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';

import '../api/api_client.dart';
import '../config/app_config.dart';
import '../firebase_options.dart';
import 'auth_storage.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  debugPrint('FCM background: ${message.notification?.title}');
}

class PushNotifications {
  PushNotifications._();
  static final PushNotifications instance = PushNotifications._();

  bool _initialized = false;
  String? _token;

  Future<void> init() async {
    if (_initialized || !AppConfig.enableFcm) return;
    _initialized = true;
    try {
      await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
      FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
      final messaging = FirebaseMessaging.instance;
      await messaging.requestPermission(alert: true, badge: true, sound: true);
      _token = await messaging.getToken();
      FirebaseMessaging.onMessage.listen((msg) {
        debugPrint('FCM foreground: ${msg.notification?.title}');
      });
    } catch (e) {
      debugPrint('PushNotifications init skipped: $e');
    }
  }

  Future<String?> getToken() async {
    if (_token != null) return _token;
    if (!AppConfig.enableFcm) return null;
    try {
      _token = await FirebaseMessaging.instance.getToken();
    } catch (_) {}
    return _token;
  }

  String get _platform {
    if (kIsWeb) return 'web';
    if (Platform.isAndroid) return 'android';
    if (Platform.isIOS) return 'ios';
    return 'unknown';
  }

  Future<void> registerWithBackend(ApiClient api) async {
    if (!AuthStorage.instance.isLoggedIn) return;
    final token = await getToken();
    if (token == null || token.length < 20) return;
    try {
      await api.registerDevice(fcmToken: token, platform: _platform);
    } catch (e) {
      debugPrint('Device register failed: $e');
    }
  }
}
