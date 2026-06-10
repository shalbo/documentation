import 'package:flutter/material.dart';

enum TrackStatus { done, current, todo }

class ServiceModel {
  final String id;
  final String slug;
  final String name;
  final String subtitle;
  final String? iconKey;
  final double priceSar;
  final int durationMinutes;

  const ServiceModel({
    required this.id,
    required this.slug,
    required this.name,
    required this.subtitle,
    this.iconKey,
    required this.priceSar,
    required this.durationMinutes,
  });

  factory ServiceModel.fromJson(Map<String, dynamic> json) {
    return ServiceModel(
      id: json['id'] as String,
      slug: json['slug'] as String,
      name: json['name_ar'] as String,
      subtitle: json['subtitle_ar'] as String? ?? '',
      iconKey: json['icon_key'] as String?,
      priceSar: (json['price_sar'] as num).toDouble(),
      durationMinutes: json['duration_minutes'] as int,
    );
  }

  IconData get icon => iconFromKey(iconKey);
  int get price => priceSar.round();
  String get duration => '$durationMinutes دقيقة';
}

class CategoryModel {
  final String id;
  final String slug;
  final String nameAr;
  final int sortOrder;
  final List<ServiceModel> services;

  const CategoryModel({
    required this.id,
    required this.slug,
    required this.nameAr,
    required this.sortOrder,
    required this.services,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    final services = (json['services'] as List<dynamic>? ?? [])
        .map((s) => ServiceModel.fromJson(s as Map<String, dynamic>))
        .toList();
    return CategoryModel(
      id: json['id'] as String,
      slug: json['slug'] as String,
      nameAr: json['name_ar'] as String,
      sortOrder: json['sort_order'] as int? ?? 0,
      services: services,
    );
  }
}

class UserModel {
  final String id;
  final String fullName;
  final String email;
  final String? avatarInitials;
  final int loyaltyPoints;
  final int servicesCount;
  final int vehiclesCount;

  const UserModel({
    required this.id,
    required this.fullName,
    required this.email,
    this.avatarInitials,
    required this.loyaltyPoints,
    this.servicesCount = 0,
    this.vehiclesCount = 0,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    final stats = json['stats'] as Map<String, dynamic>? ?? {};
    return UserModel(
      id: json['id'] as String,
      fullName: json['full_name'] as String,
      email: json['email'] as String,
      avatarInitials: json['avatar_initials'] as String?,
      loyaltyPoints: json['loyalty_points'] as int? ?? 0,
      servicesCount: stats['services_count'] as int? ?? 0,
      vehiclesCount: stats['vehicles_count'] as int? ?? 0,
    );
  }
}

class VehicleModel {
  final String id;
  final String make;
  final String model;
  final int year;
  final String? color;
  final String plateNumber;
  final bool isDefault;

  const VehicleModel({
    required this.id,
    required this.make,
    required this.model,
    required this.year,
    this.color,
    required this.plateNumber,
    this.isDefault = false,
  });

  factory VehicleModel.fromJson(Map<String, dynamic> json) {
    return VehicleModel(
      id: json['id'] as String,
      make: json['make'] as String,
      model: json['model'] as String,
      year: json['year'] as int,
      color: json['color'] as String?,
      plateNumber: json['plate_number'] as String,
      isDefault: json['is_default'] as bool? ?? false,
    );
  }

  String get displayTitle => '$make $model $year';

  String get displaySubtitle {
    final parts = <String>[];
    if (color != null && color!.isNotEmpty) parts.add(color!);
    parts.add(plateNumber);
    return parts.join(' · ');
  }
}

class AddressModel {
  final String id;
  final String label;
  final String district;
  final String city;

  const AddressModel({
    required this.id,
    required this.label,
    required this.district,
    required this.city,
  });

  factory AddressModel.fromJson(Map<String, dynamic> json) {
    return AddressModel(
      id: json['id'] as String,
      label: json['label'] as String,
      district: json['district'] as String,
      city: json['city'] as String,
    );
  }

  String get displaySubtitle => '$district، $city';
}

class PaymentMethodModel {
  final String id;
  final String labelAr;

  const PaymentMethodModel({required this.id, required this.labelAr});

  factory PaymentMethodModel.fromJson(Map<String, dynamic> json) {
    return PaymentMethodModel(
      id: json['id'] as String,
      labelAr: json['label_ar'] as String,
    );
  }
}

class BookingModel {
  final String id;
  final String reference;
  final String status;
  final String statusLabelAr;
  final String? serviceName;
  final String? serviceIconKey;

  const BookingModel({
    required this.id,
    required this.reference,
    required this.status,
    required this.statusLabelAr,
    this.serviceName,
    this.serviceIconKey,
  });

  factory BookingModel.fromJson(Map<String, dynamic> json) {
    final service = json['service'] as Map<String, dynamic>?;
    return BookingModel(
      id: json['id'] as String,
      reference: json['reference'] as String,
      status: json['status'] as String,
      statusLabelAr: json['status_label_ar'] as String? ?? '',
      serviceName: service?['name_ar'] as String?,
      serviceIconKey: service?['icon_key'] as String?,
    );
  }
}

class TrackStepModel {
  final String title;
  final String time;
  final TrackStatus status;

  const TrackStepModel({
    required this.title,
    required this.time,
    required this.status,
  });
}

class GeoLocationModel {
  final double lat;
  final double lng;

  const GeoLocationModel({required this.lat, required this.lng});

  factory GeoLocationModel.fromJson(Map<String, dynamic> json) {
    return GeoLocationModel(
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
    );
  }
}

class TrackingDestinationModel {
  final String label;
  final double lat;
  final double lng;

  const TrackingDestinationModel({
    required this.label,
    required this.lat,
    required this.lng,
  });

  factory TrackingDestinationModel.fromJson(Map<String, dynamic> json) {
    return TrackingDestinationModel(
      label: json['label'] as String,
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
    );
  }
}

class DeliveryTrailPointModel {
  final double lat;
  final double lng;

  const DeliveryTrailPointModel({required this.lat, required this.lng});

  factory DeliveryTrailPointModel.fromJson(Map<String, dynamic> json) {
    return DeliveryTrailPointModel(
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
    );
  }
}

class TechnicianModel {
  final String fullName;
  final double rating;
  final String? avatarInitials;
  final String? phone;
  final int? etaMinutes;
  final GeoLocationModel? location;

  const TechnicianModel({
    required this.fullName,
    required this.rating,
    this.avatarInitials,
    this.phone,
    this.etaMinutes,
    this.location,
  });

  factory TechnicianModel.fromJson(Map<String, dynamic> json) {
    final loc = json['location'] as Map<String, dynamic>?;
    return TechnicianModel(
      fullName: json['full_name'] as String,
      rating: (json['rating'] as num).toDouble(),
      avatarInitials: json['avatar_initials'] as String?,
      phone: json['phone'] as String?,
      etaMinutes: json['eta_minutes'] as int?,
      location: loc != null ? GeoLocationModel.fromJson(loc) : null,
    );
  }

  String get subtitle {
    final eta = etaMinutes;
    if (eta != null) return '★ $rating · يصل خلال $eta دقيقة';
    return '★ $rating';
  }
}

class PromotionModel {
  final String code;
  final String title;
  final String description;

  const PromotionModel({
    required this.code,
    required this.title,
    required this.description,
  });

  factory PromotionModel.fromJson(Map<String, dynamic> json) {
    return PromotionModel(
      code: json['code'] as String,
      title: (json['title_ar'] ?? json['title']) as String,
      description: json['description_ar'] as String? ?? '',
    );
  }
}

IconData iconFromKey(String? key) {
  switch (key) {
    case 'oil_barrel':
      return Icons.oil_barrel_outlined;
    case 'tire_repair':
      return Icons.tire_repair_outlined;
    case 'disc_full':
      return Icons.disc_full_outlined;
    case 'ac_unit':
      return Icons.ac_unit;
    case 'battery_charging':
      return Icons.battery_charging_full_outlined;
    case 'laptop_mac':
      return Icons.laptop_mac_outlined;
    case 'warning':
      return Icons.warning_amber_outlined;
    case 'water_drop':
      return Icons.water_drop_outlined;
    case 'car_crash':
      return Icons.car_crash_outlined;
    default:
      return Icons.build_outlined;
  }
}

class SplitLegPreviewModel {
  final String recipientType;
  final String labelAr;
  final double rate;
  final double amountSar;

  const SplitLegPreviewModel({
    required this.recipientType,
    required this.labelAr,
    required this.rate,
    required this.amountSar,
  });

  factory SplitLegPreviewModel.fromJson(Map<String, dynamic> json) {
    return SplitLegPreviewModel(
      recipientType: json['recipient_type'] as String,
      labelAr: json['label_ar'] as String,
      rate: (json['rate'] as num).toDouble(),
      amountSar: (json['amount_sar'] as num).toDouble(),
    );
  }
}

class SplitPreviewModel {
  final double amountSar;
  final String ruleSlug;
  final List<SplitLegPreviewModel> legs;

  const SplitPreviewModel({
    required this.amountSar,
    required this.ruleSlug,
    required this.legs,
  });

  factory SplitPreviewModel.fromJson(Map<String, dynamic> json) {
    final legsJson = json['legs'] as List<dynamic>? ?? [];
    return SplitPreviewModel(
      amountSar: (json['amount_sar'] as num).toDouble(),
      ruleSlug: json['rule_slug'] as String? ?? 'default',
      legs: legsJson
          .map((e) => SplitLegPreviewModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class ScanTypeModel {
  final String id;
  final String labelAr;
  final String descriptionAr;
  final String? iconKey;

  const ScanTypeModel({
    required this.id,
    required this.labelAr,
    required this.descriptionAr,
    this.iconKey,
  });

  factory ScanTypeModel.fromJson(Map<String, dynamic> json) {
    return ScanTypeModel(
      id: json['id'] as String,
      labelAr: json['label_ar'] as String,
      descriptionAr: json['description_ar'] as String? ?? '',
      iconKey: json['icon_key'] as String?,
    );
  }

  IconData get icon => iconFromKey(iconKey);
}

class ScanFindingModel {
  final String code;
  final String labelAr;
  final String severity;
  final double confidence;
  final ServiceModel? suggestedService;

  const ScanFindingModel({
    required this.code,
    required this.labelAr,
    required this.severity,
    required this.confidence,
    this.suggestedService,
  });

  factory ScanFindingModel.fromJson(Map<String, dynamic> json) {
    final svc = json['suggested_service'] as Map<String, dynamic>?;
    return ScanFindingModel(
      code: json['code'] as String,
      labelAr: json['label_ar'] as String,
      severity: json['severity'] as String? ?? 'medium',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0,
      suggestedService:
          svc != null ? ServiceModel.fromJson(svc) : null,
    );
  }
}

class ScanModel {
  final String id;
  final String vehicleId;
  final String scanType;
  final String status;
  final List<ScanFindingModel> findings;

  const ScanModel({
    required this.id,
    required this.vehicleId,
    required this.scanType,
    required this.status,
    required this.findings,
  });

  factory ScanModel.fromJson(Map<String, dynamic> json) {
    final findingsJson = json['findings'] as List<dynamic>? ?? [];
    return ScanModel(
      id: json['id'] as String,
      vehicleId: json['vehicle_id'] as String,
      scanType: json['scan_type'] as String,
      status: json['status'] as String? ?? 'completed',
      findings: findingsJson
          .map((e) => ScanFindingModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  ScanFindingModel? get primaryFinding =>
      findings.isNotEmpty ? findings.first : null;
}

class MembershipPlanModel {
  final String slug;
  final String nameAr;
  final String description;
  final double priceSar;
  final String billingPeriod;
  final int discountPercent;
  final bool priorityBooking;
  final bool freeInspection;

  const MembershipPlanModel({
    required this.slug,
    required this.nameAr,
    required this.description,
    required this.priceSar,
    required this.billingPeriod,
    required this.discountPercent,
    this.priorityBooking = false,
    this.freeInspection = false,
  });

  factory MembershipPlanModel.fromJson(Map<String, dynamic> json) {
    return MembershipPlanModel(
      slug: json['slug'] as String,
      nameAr: json['name_ar'] as String,
      description: json['description_ar'] as String? ?? '',
      priceSar: (json['price_sar'] as num).toDouble(),
      billingPeriod: json['billing_period'] as String? ?? 'monthly',
      discountPercent: json['discount_percent'] as int? ?? 0,
      priorityBooking: json['priority_booking'] as bool? ?? false,
      freeInspection: json['free_inspection'] as bool? ?? false,
    );
  }
}

class ServicePackageModel {
  final String slug;
  final String nameAr;
  final String description;
  final double priceSar;
  final int visitsCount;
  final double savingsSar;

  const ServicePackageModel({
    required this.slug,
    required this.nameAr,
    required this.description,
    required this.priceSar,
    required this.visitsCount,
    required this.savingsSar,
  });

  factory ServicePackageModel.fromJson(Map<String, dynamic> json) {
    return ServicePackageModel(
      slug: json['slug'] as String,
      nameAr: json['name_ar'] as String,
      description: json['description_ar'] as String? ?? '',
      priceSar: (json['price_sar'] as num).toDouble(),
      visitsCount: json['visits_count'] as int? ?? 1,
      savingsSar: (json['savings_sar'] as num?)?.toDouble() ?? 0,
    );
  }
}

class LoyaltyRewardModel {
  final String slug;
  final String title;
  final String description;
  final int pointsCost;
  final double discountSar;

  const LoyaltyRewardModel({
    required this.slug,
    required this.title,
    required this.description,
    required this.pointsCost,
    required this.discountSar,
  });

  factory LoyaltyRewardModel.fromJson(Map<String, dynamic> json) {
    return LoyaltyRewardModel(
      slug: json['slug'] as String,
      title: json['title_ar'] as String,
      description: json['description_ar'] as String? ?? '',
      pointsCost: json['points_cost'] as int,
      discountSar: (json['discount_sar'] as num).toDouble(),
    );
  }
}

class MonetizationSummary {
  final String planSlug;
  final String planNameAr;
  final int discountPercent;
  final double lifetimeSavingsSar;

  const MonetizationSummary({
    required this.planSlug,
    required this.planNameAr,
    required this.discountPercent,
    required this.lifetimeSavingsSar,
  });

  factory MonetizationSummary.fromJson(Map<String, dynamic> json) {
    final membership = json['membership'] as Map<String, dynamic>? ?? {};
    return MonetizationSummary(
      planSlug: membership['plan_slug'] as String? ?? 'free',
      planNameAr: membership['plan_name_ar'] as String? ?? 'مجاني',
      discountPercent: membership['discount_percent'] as int? ?? 0,
      lifetimeSavingsSar:
          (json['lifetime_savings_sar'] as num?)?.toDouble() ?? 0,
    );
  }
}

class HeroStatModel {
  final String slug;
  final String valueAr;
  final String labelAr;

  const HeroStatModel({
    required this.slug,
    required this.valueAr,
    required this.labelAr,
  });

  factory HeroStatModel.fromJson(Map<String, dynamic> json) {
    return HeroStatModel(
      slug: json['slug'] as String,
      valueAr: json['value_ar'] as String,
      labelAr: json['label_ar'] as String,
    );
  }
}

class MarketingPlanModel {
  final String slug;
  final String nameAr;
  final String descriptionAr;
  final double priceSar;
  final String priceLabelAr;
  final String priceDisplayAr;
  final List<String> features;
  final String ctaTextAr;
  final String? badgeAr;
  final bool isFeatured;

  const MarketingPlanModel({
    required this.slug,
    required this.nameAr,
    required this.descriptionAr,
    required this.priceSar,
    required this.priceLabelAr,
    required this.priceDisplayAr,
    required this.features,
    required this.ctaTextAr,
    this.badgeAr,
    this.isFeatured = false,
  });

  factory MarketingPlanModel.fromJson(Map<String, dynamic> json) {
    final features = (json['features'] as List<dynamic>? ?? [])
        .map((f) => f as String)
        .toList();
    return MarketingPlanModel(
      slug: json['slug'] as String,
      nameAr: json['name_ar'] as String,
      descriptionAr: json['description_ar'] as String? ?? '',
      priceSar: (json['price_sar'] as num).toDouble(),
      priceLabelAr: json['price_label_ar'] as String? ?? '',
      priceDisplayAr: json['price_display_ar'] as String? ?? '',
      features: features,
      ctaTextAr: json['cta_text_ar'] as String? ?? 'ابدأ الآن',
      badgeAr: json['badge_ar'] as String?,
      isFeatured: json['is_featured'] as bool? ?? false,
    );
  }
}

class LandingFeatureModel {
  final String slug;
  final String titleAr;
  final String descriptionAr;

  const LandingFeatureModel({
    required this.slug,
    required this.titleAr,
    required this.descriptionAr,
  });

  factory LandingFeatureModel.fromJson(Map<String, dynamic> json) {
    return LandingFeatureModel(
      slug: json['slug'] as String,
      titleAr: json['title_ar'] as String,
      descriptionAr: json['description_ar'] as String? ?? '',
    );
  }
}

class PartCategoryModel {
  final String id;
  final String slug;
  final String name;
  final String nameAr;

  const PartCategoryModel({
    required this.id,
    required this.slug,
    required this.name,
    required this.nameAr,
  });

  factory PartCategoryModel.fromJson(Map<String, dynamic> json) {
    return PartCategoryModel(
      id: json['id'] as String,
      slug: json['slug'] as String,
      name: json['name'] as String? ?? json['name_ar'] as String,
      nameAr: json['name_ar'] as String,
    );
  }
}

class PartListingModel {
  final String id;
  final String partNumber;
  final String name;
  final String nameAr;
  final double priceSar;
  final bool isOem;
  final String? categorySlug;
  final String? imageUrl;

  const PartListingModel({
    required this.id,
    required this.partNumber,
    required this.name,
    required this.nameAr,
    required this.priceSar,
    this.isOem = false,
    this.categorySlug,
    this.imageUrl,
  });

  factory PartListingModel.fromJson(Map<String, dynamic> json) {
    final category = json['category'] as Map<String, dynamic>?;
    return PartListingModel(
      id: json['id'] as String,
      partNumber: json['part_number'] as String,
      name: json['name'] as String? ?? json['name_ar'] as String,
      nameAr: json['name_ar'] as String,
      priceSar: (json['price_sar'] as num).toDouble(),
      isOem: json['is_oem'] as bool? ?? false,
      categorySlug: category?['slug'] as String?,
      imageUrl: json['image_url'] as String?,
    );
  }
}

class MarketplaceVendorModel {
  final String id;
  final String businessName;
  final String city;
  final double? distanceKm;

  const MarketplaceVendorModel({
    required this.id,
    required this.businessName,
    required this.city,
    this.distanceKm,
  });

  factory MarketplaceVendorModel.fromJson(Map<String, dynamic> json) {
    return MarketplaceVendorModel(
      id: json['id'] as String,
      businessName: json['business_name'] as String,
      city: json['city'] as String? ?? '',
      distanceKm: (json['distance_km'] as num?)?.toDouble(),
    );
  }
}

class MarketplaceHomeModel {
  final List<PartCategoryModel> categories;
  final List<PartListingModel> featuredParts;
  final List<MarketplaceVendorModel> featuredVendors;
  final List<PromotionModel> promotions;

  const MarketplaceHomeModel({
    required this.categories,
    required this.featuredParts,
    required this.featuredVendors,
    required this.promotions,
  });

  factory MarketplaceHomeModel.fromJson(Map<String, dynamic> json) {
    return MarketplaceHomeModel(
      categories: (json['categories'] as List<dynamic>? ?? [])
          .map((e) => PartCategoryModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      featuredParts: (json['featured_parts'] as List<dynamic>? ?? [])
          .map((e) => PartListingModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      featuredVendors: (json['featured_vendors'] as List<dynamic>? ?? [])
          .map((e) =>
              MarketplaceVendorModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      promotions: (json['promotions'] as List<dynamic>? ?? [])
          .map((e) => PromotionModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class LandingPricingModel {
  final List<HeroStatModel> heroStats;
  final List<MarketingPlanModel> marketingPlans;
  final List<ServiceModel> services;
  final List<ServicePackageModel> packages;
  final List<LandingFeatureModel> features;

  const LandingPricingModel({
    required this.heroStats,
    required this.marketingPlans,
    required this.services,
    required this.packages,
    required this.features,
  });
}

Color trackStatusColor(TrackStatus status) {
  switch (status) {
    case TrackStatus.done:
      return const Color(0xFF16A34A);
    case TrackStatus.current:
      return const Color(0xFFD31E28);
    case TrackStatus.todo:
      return const Color(0xFF5C7080);
  }
}
