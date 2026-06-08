import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../widgets/common.dart';

class OffersScreen extends StatelessWidget {
  const OffersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final offers = [
      ('خصم 25٪ على أول حجز', 'استخدم كود ROUSTO عند الدفع', Icons.percent),
      ('باقة الصيانة الذهبية', 'وفّر حتى 120 ريال سنوياً', Icons.workspace_premium_outlined),
      ('تغيير زيت + فحص مجاني', 'لفترة محدودة هذا الشهر', Icons.oil_barrel_outlined),
      ('اكسب نقاط مع كل خدمة', '320 نقطة متاحة الآن', Icons.card_giftcard_outlined),
    ];

    return Scaffold(
      backgroundColor: AppColors.bg,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 110),
          children: [
            const Text('العروض والمكافآت',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: AppColors.redGradient,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('رصيد نقاطك',
                      style: TextStyle(color: Color(0xFFFFE1E1))),
                  SizedBox(height: 4),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('320',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 40,
                              fontWeight: FontWeight.w800)),
                      SizedBox(width: 6),
                      Padding(
                        padding: EdgeInsets.only(bottom: 8),
                        child: Text('نقطة',
                            style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                  SizedBox(height: 6),
                  Text('تكفي لخصم 30 ريال على خدمتك القادمة',
                      style: TextStyle(color: Color(0xFFFFE1E1), fontSize: 12)),
                ],
              ),
            ),
            const SizedBox(height: 18),
            const RowHeader('عروض حصرية'),
            const SizedBox(height: 12),
            for (final o in offers) ...[
              SoftCard(
                child: Row(
                  children: [
                    IconBadge(o.$3, size: 44),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(o.$1,
                              style: const TextStyle(
                                  fontWeight: FontWeight.w800,
                                  fontSize: 14)),
                          Text(o.$2,
                              style: const TextStyle(
                                  color: AppColors.ink500, fontSize: 12)),
                        ],
                      ),
                    ),
                    const Icon(Icons.chevron_left, color: AppColors.ink300),
                  ],
                ),
              ),
              const SizedBox(height: 10),
            ],
          ],
        ),
      ),
    );
  }
}
