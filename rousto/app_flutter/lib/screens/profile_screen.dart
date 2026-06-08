import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../widgets/common.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final items = <(IconData, String, String)>[
      (Icons.directions_car_filled_outlined, 'سياراتي', 'إدارة المركبات'),
      (Icons.receipt_long_outlined, 'سجل الطلبات', '14 خدمة سابقة'),
      (Icons.credit_card, 'طرق الدفع', 'مدى، آبل باي'),
      (Icons.location_on_outlined, 'العناوين', 'المنزل، العمل'),
      (Icons.card_giftcard_outlined, 'المكافآت', '320 نقطة متاحة'),
      (Icons.settings_outlined, 'الإعدادات', 'الإشعارات واللغة'),
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
            child: const SafeArea(
              bottom: false,
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 36,
                    backgroundColor: Colors.white,
                    child: Text('س',
                        style: TextStyle(
                            color: AppColors.red600,
                            fontSize: 26,
                            fontWeight: FontWeight.w800)),
                  ),
                  SizedBox(height: 10),
                  Text('سعود العتيبي',
                      style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w800)),
                  Text('saud@example.com',
                      style: TextStyle(color: Color(0xFFFFD9DA))),
                ],
              ),
            ),
          ),
          Transform.translate(
            offset: const Offset(0, -16),
            child: const Padding(
              padding: EdgeInsets.symmetric(horizontal: 18),
              child: SoftCard(
                padding: EdgeInsets.symmetric(vertical: 14),
                child: Row(
                  children: [
                    _Stat('14', 'خدمة'),
                    _Stat('2', 'سيارة'),
                    _Stat('320', 'نقطة'),
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
                  const SizedBox(height: 10),
                ],
              ],
            ),
          ),
        ],
      ),
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
