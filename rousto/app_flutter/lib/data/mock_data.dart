import 'models.dart';

/// بيانات تجريبية تُستخدم عند عدم توفر الـ API.
class MockData {
  MockData._();

  static const user = UserModel(
    id: 'a0000000-0000-4000-8000-000000000001',
    fullName: 'سعود العتيبي',
    email: 'saud@example.com',
    avatarInitials: 'س',
    loyaltyPoints: 320,
    servicesCount: 14,
    vehiclesCount: 2,
  );

  static final categories = <CategoryModel>[
    CategoryModel(
      id: 'all',
      slug: 'all',
      nameAr: 'الكل',
      sortOrder: 0,
      services: services,
    ),
    CategoryModel(
      id: 'oil',
      slug: 'oil',
      nameAr: 'زيت',
      sortOrder: 1,
      services: [services[0]],
    ),
    CategoryModel(
      id: 'tires',
      slug: 'tires',
      nameAr: 'إطارات',
      sortOrder: 2,
      services: [services[1]],
    ),
    CategoryModel(
      id: 'brakes',
      slug: 'brakes',
      nameAr: 'فرامل',
      sortOrder: 3,
      services: [services[2]],
    ),
    CategoryModel(
      id: 'ac',
      slug: 'ac',
      nameAr: 'تكييف',
      sortOrder: 4,
      services: [services[3]],
    ),
    CategoryModel(
      id: 'electrical',
      slug: 'electrical',
      nameAr: 'كهرباء',
      sortOrder: 5,
      services: services.sublist(4),
    ),
  ];

  static final services = <ServiceModel>[
    const ServiceModel(
      id: 'f0000000-0000-4000-8000-000000000001',
      slug: 'oil-change',
      name: 'تغيير الزيت والفلاتر',
      subtitle: 'زيت أصلي + فحص شامل',
      iconKey: 'oil_barrel',
      priceSar: 120,
      durationMinutes: 45,
    ),
    const ServiceModel(
      id: 'f0000000-0000-4000-8000-000000000002',
      slug: 'tires',
      name: 'الإطارات والترصيص',
      subtitle: 'موازنة وتبديل الإطارات',
      iconKey: 'tire_repair',
      priceSar: 90,
      durationMinutes: 30,
    ),
    const ServiceModel(
      id: 'f0000000-0000-4000-8000-000000000003',
      slug: 'brakes',
      name: 'نظام الفرامل',
      subtitle: 'فحص واستبدال الفحمات',
      iconKey: 'disc_full',
      priceSar: 180,
      durationMinutes: 60,
    ),
    const ServiceModel(
      id: 'f0000000-0000-4000-8000-000000000004',
      slug: 'ac',
      name: 'تكييف وتبريد',
      subtitle: 'تعبئة فريون وصيانة',
      iconKey: 'ac_unit',
      priceSar: 150,
      durationMinutes: 50,
    ),
    const ServiceModel(
      id: 'f0000000-0000-4000-8000-000000000005',
      slug: 'battery',
      name: 'البطارية والكهرباء',
      subtitle: 'فحص وتركيب بطاريات',
      iconKey: 'battery_charging',
      priceSar: 110,
      durationMinutes: 40,
    ),
    const ServiceModel(
      id: 'f0000000-0000-4000-8000-000000000006',
      slug: 'diagnostics',
      name: 'فحص كمبيوتر شامل',
      subtitle: 'تشخيص إلكتروني دقيق',
      iconKey: 'laptop_mac',
      priceSar: 75,
      durationMinutes: 35,
    ),
  ];

  static const activeBooking = BookingModel(
    id: 'i0000000-0000-4000-8000-000000000001',
    reference: 'RST-2026-001',
    status: 'en_route',
    statusLabelAr: 'جارية',
    serviceName: 'تغيير الزيت والفلاتر',
    serviceIconKey: 'oil_barrel',
  );

  static const vehicle = VehicleModel(
    id: 'b0000000-0000-4000-8000-000000000001',
    make: 'تويوتا',
    model: 'كامري',
    year: 2022,
    color: 'أبيض',
    plateNumber: 'أ ب ج 1234',
    isDefault: true,
  );

  static const address = AddressModel(
    id: 'c0000000-0000-4000-8000-000000000001',
    label: 'المنزل',
    district: 'حي النخيل',
    city: 'الرياض',
  );

  static const paymentMethod = PaymentMethodModel(
    id: 'd0000000-0000-4000-8000-000000000001',
    labelAr: 'مدى **** 4421',
  );

  static const technician = TechnicianModel(
    fullName: 'أحمد الفني',
    rating: 4.9,
    avatarInitials: 'أ',
    phone: '+966509876543',
    etaMinutes: 12,
    location: GeoLocationModel(lat: 24.77, lng: 46.735),
  );

  static const trackingDestination = TrackingDestinationModel(
    label: 'المنزل · حي النخيل',
    lat: 24.774265,
    lng: 46.738586,
  );

  static const trackingDistanceKm = 0.42;

  static const trackSteps = <TrackStepModel>[
    TrackStepModel(title: 'تم تأكيد الحجز', time: '9:02 ص', status: TrackStatus.done),
    TrackStepModel(title: 'تم تعيين الفني', time: '9:05 ص', status: TrackStatus.done),
    TrackStepModel(
      title: 'الفني في الطريق إليك',
      time: 'الآن · 12 دقيقة',
      status: TrackStatus.current,
    ),
    TrackStepModel(title: 'تنفيذ الخدمة', time: 'قيد الانتظار', status: TrackStatus.todo),
    TrackStepModel(title: 'اكتمال الخدمة', time: 'قيد الانتظار', status: TrackStatus.todo),
  ];

  static const membershipPlans = <MembershipPlanModel>[
    MembershipPlanModel(
      slug: 'free',
      nameAr: 'مجاني',
      description: 'الخطة الأساسية — احجز وادفع لكل خدمة',
      priceSar: 0,
      billingPeriod: 'monthly',
      discountPercent: 0,
    ),
    MembershipPlanModel(
      slug: 'gold',
      nameAr: 'ذهبي',
      description: 'خصم 10٪ على كل خدمة + أولوية الحجز',
      priceSar: 29,
      billingPeriod: 'monthly',
      discountPercent: 10,
      priorityBooking: true,
    ),
    MembershipPlanModel(
      slug: 'platinum',
      nameAr: 'بلاتيني',
      description: 'خصم 20٪ + فحص مجاني سنوي + أولوية قصوى',
      priceSar: 79,
      billingPeriod: 'monthly',
      discountPercent: 20,
      priorityBooking: true,
      freeInspection: true,
    ),
  ];

  static const servicePackages = <ServicePackageModel>[
    ServicePackageModel(
      slug: 'gold-maintenance',
      nameAr: 'باقة الصيانة الذهبية',
      description: '4 زيارات صيانة سنوية — زيت + فحص + إطارات',
      priceSar: 499,
      visitsCount: 4,
      savingsSar: 120,
    ),
    ServicePackageModel(
      slug: 'basic-care',
      nameAr: 'باقة العناية الأساسية',
      description: 'زيت + فحص شامل — زيارتان',
      priceSar: 199,
      visitsCount: 2,
      savingsSar: 40,
    ),
  ];

  static const loyaltyRewards = <LoyaltyRewardModel>[
    LoyaltyRewardModel(
      slug: 'discount-10',
      title: 'خصم 10 دينار',
      description: 'استبدل 100 نقطة بخصم 10 دينار',
      pointsCost: 100,
      discountSar: 10,
    ),
    LoyaltyRewardModel(
      slug: 'discount-30',
      title: 'خصم 30 دينار',
      description: 'استبدل 300 نقطة بخصم 30 دينار',
      pointsCost: 300,
      discountSar: 30,
    ),
  ];

  static const monetization = MonetizationSummary(
    planSlug: 'free',
    planNameAr: 'مجاني',
    discountPercent: 0,
    lifetimeSavingsSar: 30,
  );

  static SplitPreviewModel splitPreviewFor(double amount) {
    final platform = (amount * 0.15).roundToDouble();
    final technician = (amount * 0.75).roundToDouble();
    final reserve = (amount - platform - technician);
    return SplitPreviewModel(
      amountSar: amount,
      ruleSlug: 'default',
      legs: [
        SplitLegPreviewModel(
          recipientType: 'platform',
          labelAr: 'عمولة المنصة',
          rate: 0.15,
          amountSar: platform,
        ),
        SplitLegPreviewModel(
          recipientType: 'technician',
          labelAr: 'حصة الفني',
          rate: 0.75,
          amountSar: technician,
        ),
        SplitLegPreviewModel(
          recipientType: 'reserve',
          labelAr: 'احتياطي المنصة',
          rate: 0.10,
          amountSar: reserve,
        ),
      ],
    );
  }

  static const scanTypes = <ScanTypeModel>[
    ScanTypeModel(
      id: 'dashboard_warning',
      labelAr: 'أضواء تحذير (الطبلون)',
      descriptionAr: 'صورة لأضواء التحذير على لوحة القيادة',
      iconKey: 'warning',
    ),
    ScanTypeModel(
      id: 'tire_tread',
      labelAr: 'الإطارات والتآكل',
      descriptionAr: 'صورة واضحة لسطح الإطار',
      iconKey: 'tire_repair',
    ),
    ScanTypeModel(
      id: 'fluid_leak',
      labelAr: 'تسرب سوائل',
      descriptionAr: 'صورة لبقعة زيت تحت السيارة',
      iconKey: 'water_drop',
    ),
    ScanTypeModel(
      id: 'battery_corrosion',
      labelAr: 'البطارية والأكسدة',
      descriptionAr: 'صورة لقطب البطارية',
      iconKey: 'battery_charging',
    ),
  ];

  static final sampleScan = ScanModel(
    id: 'mock-scan-001',
    vehicleId: vehicle.id,
    scanType: 'dashboard_warning',
    status: 'completed',
    findings: [
      ScanFindingModel(
        code: 'check_engine',
        labelAr: 'ضوء فحص المحرك — يُنصح بفحص إلكتروني',
        severity: 'medium',
        confidence: 0.82,
        suggestedService: services[5],
      ),
    ],
  );

  static const promotions = <PromotionModel>[
    PromotionModel(
      code: 'ROUSTO',
      title: 'خصم 25٪ على أول حجز',
      description: 'استخدم كود ROUSTO عند الدفع',
    ),
    PromotionModel(
      code: 'GOLD2026',
      title: 'باقة الصيانة الذهبية',
      description: 'وفّر حتى 120 دينار سنوياً',
    ),
  ];
}
