import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../currency.dart';
import '../data/models.dart';
import '../l10n/app_localizations.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'pricing_screen.dart';

class OffersScreen extends StatelessWidget {
  const OffersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

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
                    Text(l10n.offersAndSubscriptions,
                        style: const TextStyle(
                            fontSize: 20, fontWeight: FontWeight.w800)),
                    if (state.usingMockData) const DemoBadge(),
                  ],
                ),
                const SizedBox(height: 14),
                GestureDetector(
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const PricingScreen()),
                  ),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.cream,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.line),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.payments_outlined,
                            color: AppColors.red, size: 28),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(l10n.fullPricingPage,
                                  style: const TextStyle(
                                      color: AppColors.ink900,
                                      fontWeight: FontWeight.w800)),
                              Text(l10n.fullPricingSubtitle,
                                  style: const TextStyle(
                                      color: AppColors.ink500,
                                      fontSize: 12)),
                            ],
                          ),
                        ),
                        const Icon(Icons.chevron_left, color: AppColors.ink300),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                _pointsCard(context, state.loyaltyPoints),
                const SizedBox(height: 18),
                RowHeader(l10n.membershipPlans),
                const SizedBox(height: 10),
                _membershipPlans(context, state),
                const SizedBox(height: 18),
                RowHeader(l10n.maintenancePackages),
                const SizedBox(height: 10),
                for (final p in state.servicePackages) _packageCard(context, p),
                const SizedBox(height: 18),
                RowHeader(l10n.redeemPoints),
                const SizedBox(height: 10),
                for (final r in state.loyaltyRewards)
                  _rewardCard(context, state, r),
                const SizedBox(height: 18),
                RowHeader(l10n.exclusiveOffers),
                const SizedBox(height: 10),
                for (final o in state.promotions) _promoCard(o),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _pointsCard(BuildContext context, int points) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppColors.redGradient,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(l10n.yourPointsBalance,
              style: const TextStyle(color: Color(0xFFFFE1E1))),
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
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(l10n.points,
                    style: const TextStyle(color: Colors.white)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            l10n.pointsDiscountInfo(
              formatAmount(points / 10),
              formatAmount(10),
            ),
            style: const TextStyle(color: Color(0xFFFFE1E1), fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _membershipPlans(BuildContext context, AppState state) {
    final l10n = AppLocalizations.of(context)!;
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
              color: isCurrent ? AppColors.red050 : AppColors.cream,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isCurrent ? AppColors.red : AppColors.line,
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
                      ? l10n.free
                      : formatAmountPerMonth(plan.priceSar),
                  style: const TextStyle(
                      color: AppColors.red600,
                      fontWeight: FontWeight.w800,
                      fontSize: 13),
                ),
                if (!isCurrent && plan.slug != 'free') ...[
                  const SizedBox(height: 6),
                  GestureDetector(
                    onTap: () => _subscribe(context, state, plan),
                    child: Text(l10n.subscribeNow,
                        style: const TextStyle(
                            color: AppColors.red600,
                            fontWeight: FontWeight.w700,
                            fontSize: 12)),
                  ),
                ],
                if (isCurrent)
                  Text(l10n.yourCurrentPlan,
                      style: const TextStyle(
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
    final l10n = AppLocalizations.of(context)!;
    final ok = await state.subscribeToPlan(plan.slug);
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok
              ? l10n.subscribedToPlan(plan.nameAr)
              : l10n.subscribeFailed,
        ),
      ),
    );
  }

  Widget _packageCard(BuildContext context, ServicePackageModel p) {
    final l10n = AppLocalizations.of(context)!;
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
                    l10n.visitsSave(p.visitsCount, formatAmount(p.savingsSar)),
                    style: const TextStyle(
                        color: AppColors.red600,
                        fontSize: 11,
                        fontWeight: FontWeight.w700),
                  ),
                ],
              ),
            ),
            Text(formatAmount(p.priceSar),
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
    final l10n = AppLocalizations.of(context)!;
    final canRedeem = state.loyaltyPoints >= r.pointsCost;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SoftCard(
        child: Row(
          children: [
            const IconBadge(Icons.card_giftcard_outlined, size: 44),
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
                  Text(l10n.pointsCost(r.pointsCost),
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
                  child: Text(l10n.redeem,
                      style: const TextStyle(
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
    final l10n = AppLocalizations.of(context)!;
    final msg = await state.redeemReward(r.slug);
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg ?? l10n.redeemFailed),
      ),
    );
  }

  Widget _promoCard(PromotionModel o) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: SoftCard(
        child: Row(
          children: [
            const IconBadge(Icons.percent, size: 44),
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
