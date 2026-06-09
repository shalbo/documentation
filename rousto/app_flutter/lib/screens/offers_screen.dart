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

        return Scaffold(
          backgroundColor: AppColors.bg,
          body: SafeArea(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(18, 8, 18, 110),
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('العروض والاشتراكات',
                        style: TextStyle(
                            fontSize: 20, fontWeight: FontWeight.w800)),
                    if (state.usingMockData) const DemoBadge(),
                  ],
                ),
                const SizedBox(height: 14),
                _pointsCard(state.loyaltyPoints),
                const SizedBox(height: 18),
                const RowHeader('خطط العضوية'),
                const SizedBox(height: 10),
                _membershipPlans(context, state),
                const SizedBox(height: 18),
                const RowHeader('باقات الصيانة'),
                const SizedBox(height: 10),
                for (final p in state.servicePackages) _packageCard(p),
                const SizedBox(height: 18),
                const RowHeader('استبدال النقاط'),
                const SizedBox(height: 10),
                for (final r in state.loyaltyRewards)
                  _rewardCard(context, state, r),
                const SizedBox(height: 18),
                const RowHeader('عروض حصرية'),
                const SizedBox(height: 10),
                for (final o in state.promotions) _promoCard(o),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _pointsCard(int points) {
    return Container(
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
              Text('$points',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 40,
                      fontWeight: FontWeight.w800)),
              const SizedBox(width: 6),
              const Padding(
                padding: EdgeInsets.only(bottom: 8),
                child:
                    Text('نقطة', style: TextStyle(color: Colors.white)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'تكفي لخصم ${(points / 10).round()} ريال — 100 نقطة = 10 ريال',
            style: const TextStyle(color: Color(0xFFFFE1E1), fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _membershipPlans(BuildContext context, AppState state) {
    return SizedBox(
      height: 170,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: state.membershipPlans.length,
        separatorBuilder: (_, __) => const SizedBox(width: 10),
        itemBuilder: (_, i) {
          final plan = state.membershipPlans[i];
          final isCurrent =
              state.monetization?.planSlug == plan.slug;
          return Container(
            width: 160,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: isCurrent ? AppColors.red050 : AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isCurrent ? AppColors.red600 : AppColors.line,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(plan.nameAr,
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 15)),
                const SizedBox(height: 4),
                Text(plan.description,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        color: AppColors.ink500, fontSize: 11)),
                const Spacer(),
                Text(
                  plan.priceSar == 0
                      ? 'مجاني'
                      : '${plan.priceSar.round()} ريال/شهر',
                  style: const TextStyle(
                      color: AppColors.red600,
                      fontWeight: FontWeight.w800,
                      fontSize: 13),
                ),
                if (!isCurrent && plan.slug != 'free') ...[
                  const SizedBox(height: 6),
                  GestureDetector(
                    onTap: () => _subscribe(context, state, plan),
                    child: const Text('اشترك الآن',
                        style: TextStyle(
                            color: AppColors.red600,
                            fontWeight: FontWeight.w700,
                            fontSize: 12)),
                  ),
                ],
                if (isCurrent)
                  const Text('خطتك الحالية',
                      style: TextStyle(
                          color: AppColors.green,
                          fontWeight: FontWeight.w700,
                          fontSize: 11)),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _subscribe(
    BuildContext context,
    AppState state,
    MembershipPlanModel plan,
  ) async {
    final ok = await state.subscribeToPlan(plan.slug);
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok
              ? 'تم الاشتراك في خطة ${plan.nameAr}'
              : 'تعذّر الاشتراك — وضع تجريبي',
        ),
      ),
    );
  }

  Widget _packageCard(ServicePackageModel p) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SoftCard(
        child: Row(
          children: [
            const IconBadge(Icons.workspace_premium_outlined, size: 44),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(p.nameAr,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 14)),
                  Text(p.description,
                      style: const TextStyle(
                          color: AppColors.ink500, fontSize: 12)),
                  Text(
                    '${p.visitsCount} زيارات · وفّر ${p.savingsSar.round()} ريال',
                    style: const TextStyle(
                        color: AppColors.red600,
                        fontSize: 11,
                        fontWeight: FontWeight.w700),
                  ),
                ],
              ),
            ),
            Text('${p.priceSar.round()} ريال',
                style: const TextStyle(
                    fontWeight: FontWeight.w800, color: AppColors.ink900)),
          ],
        ),
      ),
    );
  }

  Widget _rewardCard(
    BuildContext context,
    AppState state,
    LoyaltyRewardModel r,
  ) {
    final canRedeem = state.loyaltyPoints >= r.pointsCost;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SoftCard(
        child: Row(
          children: [
            IconBadge(Icons.card_giftcard_outlined, size: 44),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(r.title,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 14)),
                  Text(r.description,
                      style: const TextStyle(
                          color: AppColors.ink500, fontSize: 12)),
                  Text('${r.pointsCost} نقطة',
                      style: TextStyle(
                          color: canRedeem
                              ? AppColors.red600
                              : AppColors.ink300,
                          fontSize: 11,
                          fontWeight: FontWeight.w700)),
                ],
              ),
            ),
            if (canRedeem)
              GestureDetector(
                onTap: () => _redeem(context, state, r),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.red050,
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: const Text('استبدال',
                      style: TextStyle(
                          color: AppColors.red600,
                          fontWeight: FontWeight.w800,
                          fontSize: 12)),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _redeem(
    BuildContext context,
    AppState state,
    LoyaltyRewardModel r,
  ) async {
    final msg = await state.redeemReward(r.slug);
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg ?? 'تعذّر الاستبدال'),
      ),
    );
  }

  Widget _promoCard(PromotionModel o) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SoftCard(
        child: Row(
          children: [
            IconBadge(Icons.percent, size: 44),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(o.title,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 14)),
                  Text(o.description,
                      style: const TextStyle(
                          color: AppColors.ink500, fontSize: 12)),
                ],
              ),
            ),
            const Icon(Icons.chevron_left, color: AppColors.ink300),
          ],
        ),
      ),
    );
  }
}
