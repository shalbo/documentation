import 'dart:io' show Platform;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../api/api_client.dart';
import '../config/app_config.dart';
import '../firebase_options.dart';
import '../screens/root_nav.dart';
import '../screens/tracking_screen.dart';
import 'auth_storage.dart';

final GlobalKey<NavigatorState> appNavigatorKey = GlobalKey<NavigatorState>();

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
  OverlayEntry? _bannerEntry;

  Future<void> init() async {
    if (_initialized || !AppConfig.enableFcm) return;
    _initialized = true;
    try {
      await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
      FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
      final messaging = FirebaseMessaging.instance;
      await messaging.requestPermission(alert: true, badge: true, sound: true);
      _token = await messaging.getToken();

      FirebaseMessaging.onMessage.listen(_onForegroundMessage);
      FirebaseMessaging.onMessageOpenedApp.listen(_handleDeepLink);

      final initial = await messaging.getInitialMessage();
      if (initial != null) {
        _handleDeepLink(initial);
      }
    } catch (e) {
      debugPrint('PushNotifications init skipped: $e');
    }
  }

  void _onForegroundMessage(RemoteMessage message) {
    final data = message.data;
    if (data['priority'] == 'high' || data['type'] == 'driver_towing_alert') {
      HapticFeedback.heavyImpact();
    }

    final title = message.notification?.title ?? data['title'] ?? 'Rousto';
    final body = message.notification?.body ?? data['body'] ?? '';
    _showForegroundBanner(title: title, body: body, data: data);
  }

  void _showForegroundBanner({
    required String title,
    required String body,
    required Map<String, dynamic> data,
  }) {
    final context = appNavigatorKey.currentContext;
    if (context == null) return;

    _bannerEntry?.remove();
    final overlay = Overlay.of(context);

    _bannerEntry = OverlayEntry(
      builder: (ctx) => Positioned(
        top: MediaQuery.of(ctx).padding.top + 8,
        left: 12,
        right: 12,
        child: Material(
          elevation: 6,
          borderRadius: BorderRadius.circular(12),
          color: const Color(0xFF0B2C44),
          child: InkWell(
            onTap: () {
              _bannerEntry?.remove();
              _bannerEntry = null;
              _handleDeepLink(RemoteMessage(data: data));
            },
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(title,
                            style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w800)),
                        if (body.isNotEmpty)
                          Text(body,
                              style: const TextStyle(
                                  color: Color(0xFFFFD9DA), fontSize: 13)),
                      ],
                    ),
                  ),
                  const Icon(Icons.chevron_left, color: Colors.white70),
                ],
              ),
            ),
          ),
        ),
      ),
    );
    overlay.insert(_bannerEntry!);
    Future.delayed(const Duration(seconds: 5), () {
      _bannerEntry?.remove();
      _bannerEntry = null;
    });
  }

  void _handleDeepLink(RemoteMessage message) {
    final type = message.data['type'] ?? '';
    final nav = appNavigatorKey.currentState;
    if (nav == null) return;

    switch (type) {
      case 'booking_status':
      case 'vendor_new_booking':
        nav.push(
          MaterialPageRoute(
            builder: (_) => const RootNav(),
          ),
        );
        break;
      case 'towing_status':
      case 'driver_towing_alert':
        nav.push(
          MaterialPageRoute(
            builder: (_) => const TrackingScreen(active: true),
          ),
        );
        break;
      case 'support_reply':
        nav.push(MaterialPageRoute(builder: (_) => const RootNav()));
        break;
      default:
        break;
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
