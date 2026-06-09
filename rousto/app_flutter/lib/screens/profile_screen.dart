import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'notifications_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, state, _) {
        if (state.loading) {
          return const Scaffold(
            backgroundColor: AppColors.bg,
            body: Center(child: CircularProgressIndicator()),
          );
        }

        final user = state.user;
        final mon = state.monetization;
        final items = <(IconData, String, String)>[
          (
            Icons.directions_car_filled_outlined,
            'سياراتي',
            '${user?.vehiclesCount ?? 0} مركبة'
          ),
          (
            Icons.receipt_long_outlined,
            'سجل الطلبات',
            '${user?.servicesCount ?? 0} خدمة سابقة'
          ),
          (Icons.credit_card, 'طرق الدفع', 'مدى، آبل باي'),
          (Icons.location_on_outlined, 'العناوين', 'المنزل، العمل'),
          (
            Icons.card_giftcard_outlined,
            'المكافآت',
            '${state.loyaltyPoints} نقطة متاحة'
          ),
          (Icons.settings_outlined, 'الإعدادات', 'الإشعارات واللغة'),
          (
            Icons.support_agent_outlined,
            'الدعم والأمان',
            'تذاكر الدعم والأسئلة الشائعة'
          ),
        ];

        return Scaffold(
          backgroundColor: AppColors.bg,
          body: ListView(
            padding: const EdgeInsets.only(bottom: 110),
            children: [
              Container(
                padding: const EdgeInsets.fromLTRB(18, 0, 18, 30),
                decoration: const BoxDecoration(
                  gradient: AppColors.redGradient,
                  borderRadius:
                      BorderRadius.vertical(bottom: Radius.circular(28)),
                ),
                child: SafeArea(
                  bottom: false,
                  child: Column(
                    children: [
                      if (state.usingMockData) const DemoBadge(),
                      if (state.usingMockData) const SizedBox(height: 8),
                      CircleAvatar(
                        radius: 36,
                        backgroundColor: Colors.white,
                        child: Text(
                          user?.avatarInitials ?? '؟',
                          style: const TextStyle(
                              color: AppColors.red600,
                              fontSize: 26,
                              fontWeight: FontWeight.w800),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        user?.fullName ?? 'ضيف',
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w800),
                      ),
                      Text(
                        user?.email ?? '',
                        style: const TextStyle(color: Color(0xFFFFD9DA)),
                      ),
                      if (mon != null) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white24,
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Text(
                            'عضوية ${mon.planNameAr}'
                                '${mon.discountPercent > 0 ? ' · خصم ${mon.discountPercent}٪' : ''}',
                            style: const TextStyle(
                                color: Colors.white, fontSize: 12),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              Transform.translate(
                offset: const Offset(0, -16),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 18),
                  child: SoftCard(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    child: Row(
                      children: [
                        _Stat('${user?.servicesCount ?? 0}', 'خدمة'),
                        _Stat('${user?.vehiclesCount ?? 0}', 'سيارة'),
                        _Stat('${state.loyaltyPoints}', 'نقطة'),
                        _Stat(
                          '${mon?.lifetimeSavingsSar.round() ?? 0}',
                          'توفير',
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 18),
                child: Column(
                  children: [
                    for (final it in items) ...[
                      SoftCard(
                        child: InkWell(
                          onTap: it.$2 == 'الإعدادات'
                              ? () => Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (_) =>
                                          const NotificationsScreen(),
                                    ),
                                  )
                              : null,
                          borderRadius: BorderRadius.circular(16),
                          child: Row(
                            children: [
                              IconBadge(it.$1, size: 40),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(it.$2,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.w800,
                                            fontSize: 14)),
                                    Text(it.$3,
                                        style: const TextStyle(
                                            color: AppColors.ink500,
                                            fontSize: 12)),
                                  ],
                                ),
                              ),
                              const Icon(Icons.chevron_left,
                                  color: AppColors.ink300),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                    ],
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _Stat extends StatelessWidget {
  final String value;
  final String label;
  const _Stat(this.value, this.label);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Text(value,
              style: const TextStyle(
                  color: AppColors.red600,
                  fontSize: 18,
                  fontWeight: FontWeight.w800)),
          Text(label,
              style: const TextStyle(
                  color: AppColors.ink500, fontSize: 12)),
        ],
      ),
    );
  }
}
