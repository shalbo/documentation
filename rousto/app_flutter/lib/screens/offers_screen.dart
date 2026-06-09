import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../data/models.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';

class OffersScreen extends StatelessWidget {
  const OffersScreen({super.key});

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

        final offers = state.promotions;
        final extra = PromotionModel(
          code: 'POINTS',
          title: 'اكسب نقاط مع كل خدمة',
          description: '${state.loyaltyPoints} نقطة متاحة الآن',
        );
        final allOffers = [...offers, extra];

        return Scaffold(
          backgroundColor: AppColors.bg,
          body: SafeArea(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(18, 8, 18, 110),
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('العروض والمكافآت',
                        style: TextStyle(
                            fontSize: 20, fontWeight: FontWeight.w800)),
                    if (state.usingMockData) const DemoBadge(),
                  ],
                ),
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    gradient: AppColors.redGradient,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('رصيد نقاطك',
                          style: TextStyle(color: Color(0xFFFFE1E1))),
                      const SizedBox(height: 4),
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text('${state.loyaltyPoints}',
                              style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 40,
                                  fontWeight: FontWeight.w800)),
                          const SizedBox(width: 6),
                          const Padding(
                            padding: EdgeInsets.only(bottom: 8),
                            child: Text('نقطة',
                                style: TextStyle(color: Colors.white)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      const Text('تكفي لخصم 30 ريال على خدمتك القادمة',
                          style: TextStyle(
                              color: Color(0xFFFFE1E1), fontSize: 12)),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                const RowHeader('عروض حصرية'),
                const SizedBox(height: 12),
                for (final o in allOffers) ...[
                  SoftCard(
                    child: Row(
                      children: [
                        IconBadge(_iconFor(o.code), size: 44),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(o.title,
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w800,
                                      fontSize: 14)),
                              Text(o.description,
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
        );
      },
    );
  }

  IconData _iconFor(String code) {
    switch (code.toUpperCase()) {
      case 'ROUSTO':
        return Icons.percent;
      case 'GOLD2026':
        return Icons.workspace_premium_outlined;
      case 'POINTS':
        return Icons.card_giftcard_outlined;
      default:
        return Icons.local_offer_outlined;
    }
  }
}
