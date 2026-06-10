import '../../../../core/network/api_client.dart';

/// In-app notifications and preferences.
class NotificationRepository {
  NotificationRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<List<Map<String, dynamic>>> getNotifications({
    bool unreadOnly = false,
    String? category,
  }) {
    return _api.getNotifications(unreadOnly: unreadOnly, category: category);
  }

  Future<int> getUnreadCount() {
    return _api.getNotificationUnreadCount();
  }

  Future<List<Map<String, dynamic>>> getPreferences() {
    return _api.getNotificationPreferences();
  }

  Future<void> markRead(String id) {
    return _api.markNotificationRead(id);
  }

  Future<void> markAllRead() {
    return _api.markAllNotificationsRead();
  }

  Future<void> updatePreferences(List<Map<String, dynamic>> preferences) {
    return _api.updateNotificationPreferences(preferences);
  }
}
