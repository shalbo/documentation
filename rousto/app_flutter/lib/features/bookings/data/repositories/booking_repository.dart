import '../../../../core/network/api_client.dart';

/// Booking creation, active booking, and tracking.
class BookingRepository {
  BookingRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<Map<String, dynamic>?> getActiveBooking() {
    return _api.getActiveBooking();
  }

  Future<Map<String, dynamic>> createBooking(Map<String, dynamic> payload) {
    return _api.createBooking(payload);
  }

  Future<Map<String, dynamic>> getTracking(String bookingId) {
    return _api.getBookingTracking(bookingId);
  }

  Future<Map<String, dynamic>> getDeliveryMap(String bookingId) {
    return _api.getBookingDeliveryMap(bookingId);
  }

  Future<List<dynamic>> getVehicles() {
    return _api.getVehicles();
  }

  Future<List<dynamic>> getAddresses() {
    return _api.getAddresses();
  }

  Future<List<dynamic>> getPaymentMethods() {
    return _api.getPaymentMethods();
  }

  Future<Map<String, dynamic>> validatePromotion(String code, double price) {
    return _api.validatePromotion(code, price);
  }

  Future<Map<String, dynamic>> previewPaymentSplit(double amountSar) {
    return _api.previewPaymentSplit(amountSar);
  }
}
