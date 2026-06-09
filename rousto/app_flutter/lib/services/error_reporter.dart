import 'dart:async';

import 'package:flutter/foundation.dart';

/// Central error reporting — wire to Sentry or Firebase Crashlytics in production.
class ErrorReporter {
  ErrorReporter._();
  static final ErrorReporter instance = ErrorReporter._();

  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;
    if (kReleaseMode) {
      // Production: SentryFlutter.init(...) or FirebaseCrashlytics.instance
      debugPrint('ErrorReporter: release mode — connect Sentry/Crashlytics');
    }
  }

  void capture(Object error, StackTrace stack, {String? hint}) {
    if (kDebugMode) {
      debugPrint('ErrorReporter: $error\n$stack');
      return;
    }
    // Production SDK capture here
    debugPrint('ErrorReporter captured: $hint — $error');
  }
}

void runRoustoApp(void Function() appRunner) {
  runZonedGuarded(
    appRunner,
    (error, stack) => ErrorReporter.instance.capture(error, stack),
  );
}
