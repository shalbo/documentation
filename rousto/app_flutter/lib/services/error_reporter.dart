import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

import '../config/app_config.dart';

class ErrorReporter {
  ErrorReporter._();
  static final ErrorReporter instance = ErrorReporter._();

  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;
  }

  void capture(Object error, StackTrace stack, {String? hint}) {
    if (kDebugMode) {
      debugPrint('ErrorReporter: $error\n$stack');
      return;
    }
    if (AppConfig.sentryDsn.isNotEmpty) {
      Sentry.captureException(error, stackTrace: stack, hint: hint);
    }
  }
}
