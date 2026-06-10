import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../config/app_config.dart';

class RegistrationService {
  RegistrationService({String? baseUrl})
      : _base = baseUrl ?? AppConfig.apiBaseUrl;

  final String _base;

  Future<List<String>> fetchCities() async {
    final res = await http.get(Uri.parse('$_base/api/v1/registration/cities'));
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      throw Exception(_msg(body));
    }
    return (body['data'] as List<dynamic>).cast<String>();
  }

  Future<Map<String, dynamic>> registerCustomer({
    required String fullName,
    required String phone,
    required String city,
  }) async {
    return _post('/api/v1/registration/customer', {
      'full_name': fullName,
      'phone': phone,
      'city': city,
    });
  }

  Future<Map<String, dynamic>> registerDriverStep1({
    required String fullName,
    required String phone,
    required String city,
    required String serviceType,
    required String plateNumber,
  }) async {
    return _post('/api/v1/registration/driver', {
      'full_name': fullName,
      'phone': phone,
      'city': city,
      'service_type': serviceType,
      'plate_number': plateNumber,
    });
  }

  Future<Map<String, dynamic>> uploadDriverDocuments({
    required String profileId,
    required List<int> licenseBytes,
    required List<int> idBytes,
    required List<int> vehicleBytes,
    String licenseName = 'license.jpg',
    String idName = 'id.jpg',
    String vehicleName = 'vehicle.jpg',
  }) async {
    final req = http.MultipartRequest(
      'POST',
      Uri.parse('$_base/api/v1/registration/driver/$profileId/documents'),
    );
    req.files.add(http.MultipartFile.fromBytes(
      'license_doc',
      licenseBytes,
      filename: licenseName,
      contentType: MediaType('image', 'jpeg'),
    ));
    req.files.add(http.MultipartFile.fromBytes(
      'id_doc',
      idBytes,
      filename: idName,
      contentType: MediaType('image', 'jpeg'),
    ));
    req.files.add(http.MultipartFile.fromBytes(
      'vehicle_doc',
      vehicleBytes,
      filename: vehicleName,
      contentType: MediaType('image', 'jpeg'),
    ));
    final streamed = await req.send();
    final res = await http.Response.fromStream(streamed);
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      throw Exception(_msg(body));
    }
    return body;
  }

  Future<double> fetchDriverRegistrationFee() async {
    return 150.0;
  }

  Future<Map<String, dynamic>> initiateDriverRegistrationPayment({
    required String profileId,
    required String phone,
    required String gateway,
    String returnUrl = 'rousto://payment/return',
  }) async {
    return _post('/api/v1/auth/register/driver/initiate-payment', {
      'profile_id': profileId,
      'phone': phone,
      'gateway': gateway,
      'return_url': returnUrl,
    });
  }

  Future<Map<String, dynamic>> getDriverPaymentStatus({
    required String profileId,
    required String phone,
  }) async {
    final uri = Uri.parse(
      '$_base/api/v1/auth/register/driver/$profileId/payment-status?phone=${Uri.encodeComponent(phone)}',
    );
    final res = await http.get(uri);
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      throw Exception(_msg(body));
    }
    return body;
  }

  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> payload) async {
    final res = await http.post(
      Uri.parse('$_base$path'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    if (res.statusCode >= 400) {
      throw Exception(_msg(body));
    }
    return body;
  }

  String _msg(Map<String, dynamic> body) {
    final detail = body['detail'];
    if (detail is Map && detail['message'] != null) {
      return detail['message'] as String;
    }
    return body['message'] as String? ?? 'فشل التسجيل';
  }
}
