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

  static const apiPrefix = '/api/v1';
}
