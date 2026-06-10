import '../../../../core/network/api_client.dart';

/// Support tickets and FAQ (customer messaging layer).
class SupportRepository {
  SupportRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<List<dynamic>> getFaq({String? category}) {
    return _api.getSupportFaq(category: category);
  }

  Future<Map<String, dynamic>> createTicket({
    required String category,
    required String subject,
    required String message,
    String priority = 'normal',
    String? bookingId,
  }) {
    return _api.createSupportTicket(
      category: category,
      subject: subject,
      message: message,
      priority: priority,
      bookingId: bookingId,
    );
  }

  Future<List<dynamic>> getMyTickets() {
    return _api.getSupportTickets();
  }

  Future<Map<String, dynamic>> getTicket(String ticketId) {
    return _api.getSupportTicket(ticketId);
  }

  Future<Map<String, dynamic>> addMessage(String ticketId, String message) {
    return _api.addSupportTicketMessage(ticketId, message);
  }
}
