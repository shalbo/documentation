class AppConfig {
  AppConfig._();

  static const defaultUserId = 'a0000000-0000-4000-8000-000000000001';

  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static const accessToken = String.fromEnvironment(
    'ACCESS_TOKEN',
    defaultValue: '',
  );

  static const useLegacyUserHeader = bool.fromEnvironment(
    'USE_LEGACY_USER_HEADER',
    defaultValue: true,
  );

  static const enableFcm = bool.fromEnvironment(
    'ENABLE_FCM',
    defaultValue: false,
  );

  static const sentryDsn = String.fromEnvironment(
    'SENTRY_DSN',
    defaultValue: '',
  );

  static const environment = String.fromEnvironment(
    'ENVIRONMENT',
    defaultValue: 'development',
  );

  static bool get isProduction {
    final e = environment.toLowerCase();
    return e == 'production' || e == 'prod';
  }

  static const apiPrefix = '/api/v1';
}
