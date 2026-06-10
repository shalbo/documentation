import '../../../../core/network/api_client.dart';

/// Payments feature repository — isolates API calls from UI/state layers.
class PaymentRepository {
  PaymentRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<Map<String, dynamic>> getCheckoutOptions() {
    return _api.getLibyanCheckoutOptions();
  }

  Future<Map<String, dynamic>> getWallet() {
    return _api.getMyWallet();
  }

  Future<Map<String, dynamic>> checkout({
    required double amountLyd,
    required String gateway,
    required String orderType,
    String? orderId,
    String? vendorId,
  }) {
    return _api.checkoutLibyan(
      amountLyd: amountLyd,
      gateway: gateway,
      orderType: orderType,
      orderId: orderId,
      vendorId: vendorId,
    );
  }

  Future<Map<String, dynamic>> initiateMuamalat({
    required double amountLyd,
    required String orderType,
    String? orderId,
    String? vendorId,
  }) {
    return _api.initiateGatewayPayment(
      gateway: 'muamalat',
      amountLyd: amountLyd,
      orderType: orderType,
      orderId: orderId,
      vendorId: vendorId,
    );
  }

  Future<Map<String, dynamic>> generatePaymentOtp({
    required String orderId,
    double? amountLyd,
  }) {
    return _api.generatePaymentOtp(orderId: orderId, amountLyd: amountLyd);
  }

  Future<Map<String, dynamic>> verifyPaymentOtp({
    required String orderId,
    required String code,
  }) {
    return _api.verifyPaymentOtp(orderId: orderId, code: code);
  }

  Future<Map<String, dynamic>> initiateSadad({
    required double amountLyd,
    required String orderType,
    String? orderId,
    String? vendorId,
  }) {
    return _api.initiateGatewayPayment(
      gateway: 'sadad',
      amountLyd: amountLyd,
      orderType: orderType,
      orderId: orderId,
      vendorId: vendorId,
    );
  }
}
