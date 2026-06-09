import '../api/api_client.dart';
import 'mock_data.dart';
import 'models.dart';

class AppRepository {
  AppRepository({ApiClient? api}) : _api = api ?? ApiClient();

  final ApiClient _api;

  Future<bool> isApiAvailable() => _api.ping();

  Future<List<CategoryModel>> loadCategories() async {
    try {
      final data = await _api.getCategoriesTree();
      return data
          .map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return MockData.categories;
    }
  }

  Future<UserModel> loadUser() async {
    try {
      final data = await _api.getMe();
      if (data != null) return UserModel.fromJson(data);
    } catch (_) {}
    return MockData.user;
  }

  Future<BookingModel?> loadActiveBooking() async {
    try {
      final data = await _api.getActiveBooking();
      if (data != null) return BookingModel.fromJson(data);
      return null;
    } catch (_) {
      return MockData.activeBooking;
    }
  }

  Future<({BookingModel booking, TechnicianModel? technician, List<TrackStepModel> steps})>
      loadTracking(String bookingId) async {
    try {
      final data = await _api.getBookingTracking(bookingId);
      final bookingJson = data['booking'] as Map<String, dynamic>;
      final booking = BookingModel(
        id: bookingId,
        reference: bookingJson['reference'] as String,
        status: bookingJson['status'] as String,
        statusLabelAr: bookingJson['status_label_ar'] as String? ?? '',
      );

      TechnicianModel? technician;
      final techJson = data['technician'] as Map<String, dynamic>?;
      if (techJson != null) technician = TechnicianModel.fromJson(techJson);

      final stepsJson = data['steps'] as List<dynamic>? ?? [];
      final steps = stepsJson.map((step) {
        final s = step as Map<String, dynamic>;
        final isCurrent = s['is_current'] as bool? ?? false;
        final isDone = s['is_done'] as bool? ?? false;
        final TrackStatus status;
        if (isCurrent) {
          status = TrackStatus.current;
        } else if (isDone) {
          status = TrackStatus.done;
        } else {
          status = TrackStatus.todo;
        }
        final occurredAt = s['occurred_at'] as String? ?? '';
        return TrackStepModel(
          title: s['label_ar'] as String,
          time: _formatTime(occurredAt, isCurrent),
          status: status,
        );
      }).toList();

      return (booking: booking, technician: technician, steps: steps);
    } catch (_) {
      return (
        booking: MockData.activeBooking,
        technician: MockData.technician,
        steps: MockData.trackSteps,
      );
    }
  }

  Future<List<PromotionModel>> loadPromotions() async {
    try {
      final data = await _api.getPromotions();
      return data
          .map((e) => PromotionModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return MockData.promotions;
    }
  }

  Future<int> loadLoyaltyBalance() async {
    try {
      final data = await _api.getLoyalty();
      return data['balance'] as int? ?? MockData.user.loyaltyPoints;
    } catch (_) {
      return MockData.user.loyaltyPoints;
    }
  }

  Future<({
    VehicleModel vehicle,
    AddressModel address,
    PaymentMethodModel payment,
  })> loadBookingContext() async {
    try {
      final vehicles = await _api.getVehicles();
      final addresses = await _api.getAddresses();
      final payments = await _api.getPaymentMethods();

      final vehicleJson = vehicles.firstWhere(
        (v) => (v as Map<String, dynamic>)['is_default'] == true,
        orElse: () => vehicles.first,
      ) as Map<String, dynamic>;
      final addressJson = addresses.firstWhere(
        (a) => (a as Map<String, dynamic>)['is_default'] == true,
        orElse: () => addresses.first,
      ) as Map<String, dynamic>;
      final paymentJson = payments.firstWhere(
        (p) => (p as Map<String, dynamic>)['is_default'] == true,
        orElse: () => payments.first,
      ) as Map<String, dynamic>;

      return (
        vehicle: VehicleModel.fromJson(vehicleJson),
        address: AddressModel.fromJson(addressJson),
        payment: PaymentMethodModel.fromJson(paymentJson),
      );
    } catch (_) {
      return (
        vehicle: MockData.vehicle,
        address: MockData.address,
        payment: MockData.paymentMethod,
      );
    }
  }

  Future<({bool valid, double discount, double total})> validatePromo(
    String code,
    double price,
  ) async {
    try {
      final data = await _api.validatePromotion(code, price);
      return (
        valid: data['valid'] as bool? ?? false,
        discount: (data['discount_sar'] as num?)?.toDouble() ?? 0,
        total: (data['total_sar'] as num?)?.toDouble() ?? price,
      );
    } catch (_) {
      if (code.toUpperCase() == 'ROUSTO') {
        return (valid: true, discount: 30, total: price - 30);
      }
      return (valid: false, discount: 0, total: price);
    }
  }

  Future<List<MembershipPlanModel>> loadMembershipPlans() async {
    try {
      final data = await _api.getMembershipPlans();
      return data
          .map((e) => MembershipPlanModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return MockData.membershipPlans;
    }
  }

  Future<List<ServicePackageModel>> loadServicePackages() async {
    try {
      final data = await _api.getServicePackages();
      return data
          .map((e) => ServicePackageModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return MockData.servicePackages;
    }
  }

  Future<List<LoyaltyRewardModel>> loadLoyaltyRewards() async {
    try {
      final data = await _api.getLoyaltyRewards();
      return data
          .map((e) => LoyaltyRewardModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return MockData.loyaltyRewards;
    }
  }

  Future<MonetizationSummary> loadMonetizationSummary() async {
    try {
      final data = await _api.getMonetizationSummary();
      return MonetizationSummary.fromJson(data);
    } catch (_) {
      return MockData.monetization;
    }
  }

  Future<bool> subscribePlan(String planSlug) async {
    try {
      await _api.subscribeMembership(planSlug);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<({bool ok, int balance, double discount})> redeemReward(
    String rewardSlug,
  ) async {
    try {
      final data = await _api.redeemReward(rewardSlug);
      return (
        ok: true,
        balance: data['balance_remaining'] as int? ?? 0,
        discount: (data['discount_sar'] as num?)?.toDouble() ?? 0,
      );
    } catch (_) {
      return (ok: false, balance: MockData.user.loyaltyPoints, discount: 0);
    }
  }

  Future<List<ScanTypeModel>> loadScanTypes() async {
    try {
      final data = await _api.getScanTypes();
      return data
          .map((e) => ScanTypeModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return MockData.scanTypes;
    }
  }

  Future<ScanModel> submitScan({
    required String vehicleId,
    required String scanType,
    required List<int> imageBytes,
    required String filename,
  }) async {
    try {
      final data = await _api.createScan(
        vehicleId: vehicleId,
        scanType: scanType,
        imageBytes: imageBytes,
        filename: filename,
      );
      return ScanModel.fromJson(data);
    } catch (_) {
      return MockData.sampleScan;
    }
  }

  Future<bool> createBooking({
    required String serviceId,
    required String vehicleId,
    required String addressId,
    String? paymentMethodId,
    String? promotionCode,
    String? scanId,
  }) async {
    try {
      await _api.createBooking({
        'service_id': serviceId,
        'vehicle_id': vehicleId,
        'address_id': addressId,
        if (paymentMethodId != null) 'payment_method_id': paymentMethodId,
        if (promotionCode != null) 'promotion_code': promotionCode,
        if (scanId != null) 'scan_id': scanId,
        'scheduled_at': DateTime.now()
            .add(const Duration(days: 1))
            .toUtc()
            .toIso8601String(),
      });
      return true;
    } catch (_) {
      return false;
    }
  }

  String _formatTime(String iso, bool isCurrent) {
    if (isCurrent) return 'الآن';
    if (iso.isEmpty) return 'قيد الانتظار';
    try {
      final dt = DateTime.parse(iso).toLocal();
      final hour = dt.hour > 12 ? dt.hour - 12 : dt.hour;
      final period = dt.hour >= 12 ? 'م' : 'ص';
      return '$hour:${dt.minute.toString().padLeft(2, '0')} $period';
    } catch (_) {
      return iso;
    }
  }
}
