import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

import 'config/app_config.dart';
import 'l10n/app_localizations.dart';
import 'screens/login_screen.dart';
import 'screens/root_nav.dart';
import 'services/auth_storage.dart';
import 'services/error_reporter.dart';
import 'services/push_notifications.dart' show PushNotifications, appNavigatorKey;
import 'state/app_state.dart';
import 'state/locale_state.dart';
import 'theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AuthStorage.instance.init();
  await ErrorReporter.instance.init();
  await PushNotifications.instance.init();

  if (AppConfig.sentryDsn.isNotEmpty) {
    await SentryFlutter.init(
      (options) {
        options.dsn = AppConfig.sentryDsn;
        options.environment = AppConfig.environment;
        options.tracesSampleRate = AppConfig.isProduction ? 0.1 : 0.0;
      },
      appRunner: () => runApp(const RoustoApp()),
    );
    return;
  }

  runZonedGuarded(
    () => runApp(const RoustoApp()),
    (error, stack) => ErrorReporter.instance.capture(error, stack),
  );
}

class RoustoApp extends StatelessWidget {
  const RoustoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AppState()..load()),
        ChangeNotifierProvider(create: (_) => LocaleState()..load()),
      ],
      child: Consumer<LocaleState>(
        builder: (context, localeState, _) {
          return MaterialApp(
            navigatorKey: appNavigatorKey,
            title: 'Rousto',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.light,
            locale: localeState.locale,
            supportedLocales: AppLocalizations.supportedLocales,
            localizationsDelegates: const [
              AppLocalizations.delegate,
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            builder: (context, child) {
              final isRtl = localeState.isRtl;
              return Directionality(
                textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
                child: child!,
              );
            },
            home: AuthStorage.instance.isLoggedIn
                ? const RootNav()
                : const LoginScreen(),
          );
        },
      ),
    );
  }
}
