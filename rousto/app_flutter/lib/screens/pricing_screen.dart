import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';

import '../currency.dart';
import '../data/app_repository.dart';
import '../data/models.dart';
import '../l10n/app_localizations.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'booking_screen.dart';

class PricingScreen extends StatefulWidget {
  const PricingScreen({super.key});

  @override
  State<PricingScreen> createState() => _PricingScreenState();
}

class _PricingScreenState extends State<PricingScreen> {
  final _repository = AppRepository();
  bool _loading = true;
  LandingPricingModel? _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final data = await _repository.loadLandingPricing();
    if (!mounted) return;
    setState(() {
      _data = data;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      backgroundColor: AppColors.bg,
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              color: AppColors.red,
              child: ListView(
                padding: const EdgeInsets.only(bottom: 32),
                children: [
                  _hero(l10n, _data!),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(18, 20, 18, 0),
                    child: RowHeader(l10n.subscriptionPlans),
                  ),
                  const SizedBox(height: 12),
                  _plans(_data!.marketingPlans),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(18, 24, 18, 0),
                    child: RowHeader(l10n.maintenancePackages),
                  ),
                  const SizedBox(height: 10),
                  ..._data!.packages.map((p) => _packageTile(context, p)),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(18, 24, 18, 0),
                    child: RowHeader(l10n.servicePrices),
                  ),
                  const SizedBox(height: 10),
                  _servicesGrid(_data!.services),
                  if (_data!.features.isNotEmpty) ...[
                    Padding(
                      padding: const EdgeInsets.fromLTRB(18, 24, 18, 0),
                      child: RowHeader(l10n.whyRousto),
                    ),
                    const SizedBox(height: 10),
                    _features(_data!.features),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _hero(AppLocalizations l10n, LandingPricingModel data) {
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 0, 18, 28),
      decoration: const BoxDecoration(
        gradient: AppColors.redGradient,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
      ),
      child: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  icon: const Icon(Icons.arrow_forward, color: Colors.white),
                ),
                SvgPicture.asset('assets/logo.svg', height: 28),
                const SizedBox(width: 8),
                Text(l10n.pricing,
                    style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 18)),
              ],
            ),
            const SizedBox(height: 8),
            Text(l10n.plansForEveryNeed,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.w800)),
            const SizedBox(height: 6),
            Text(l10n.transparentPricing,
                style: const TextStyle(color: Color(0xFFFFE1E1), fontSize: 13)),
            const SizedBox(height: 18),
            Wrap(
              spacing: 20,
              runSpacing: 10,
              children: data.heroStats
                  .map((s) => Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(s.valueAr,
                              style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 22,
                                  fontWeight: FontWeight.w800)),
                          Text(s.labelAr,
                              style: const TextStyle(
                                  color: Color(0xFFFFE1E1), fontSize: 12)),
                        ],
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _plans(List<MarketingPlanModel> plans) {
    return SizedBox(
      height: 280,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 18),
        scrollDirection: Axis.horizontal,
        itemCount: plans.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (_, i) => _planCard(plans[i]),
      ),
    );
  }

  Widget _planCard(MarketingPlanModel plan) {
    return SizedBox(
      width: 220,
      child: SoftCard(
        featured: plan.isFeatured,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (plan.badgeAr != null)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  gradient: AppColors.redGradient,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(plan.badgeAr!,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.w800)),
              ),
            if (plan.badgeAr != null) const SizedBox(height: 8),
            Text(plan.nameAr,
                style: const TextStyle(
                    fontWeight: FontWeight.w800, fontSize: 18)),
            const SizedBox(height: 4),
            Text(plan.descriptionAr,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: AppColors.ink500, fontSize: 12)),
            const SizedBox(height: 12),
            Text(plan.priceDisplayAr,
                style: const TextStyle(
                    color: AppColors.red,
                    fontSize: 26,
                    fontWeight: FontWeight.w800)),
            Text(plan.priceLabelAr,
                style: const TextStyle(color: AppColors.ink500, fontSize: 12)),
            const SizedBox(height: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: plan.features
                    .take(3)
                    .map((f) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              const Icon(Icons.check,
                                  color: AppColors.red, size: 14),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(f,
                                    style: const TextStyle(
                                        fontSize: 11,
                                        color: AppColors.ink700)),
                              ),
                            ],
                          ),
                        ))
                    .toList(),
              ),
            ),
            GradientButton(
              label: plan.ctaTextAr,
              onPressed: () => _onPlanTap(plan),
            ),
          ],
        ),
      ),
    );
  }

  void _onPlanTap(MarketingPlanModel plan) {
    final l10n = AppLocalizations.of(context)!;
    if (plan.slug == 'individual') {
      Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const BookingScreen()),
      );
      return;
    }
    final state = context.read<AppState>();
    final slug = plan.slug == 'family' ? 'gold' : 'platinum';
    state.subscribeToPlan(slug).then((ok) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(ok
              ? l10n.subscribedToPlan(plan.nameAr)
              : l10n.subscribeFailed),
        ),
      );
    });
  }

  Widget _packageTile(BuildContext context, ServicePackageModel p) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.fromLTRB(18, 0, 18, 10),
      child: SoftCard(
        child: Row(
          children: [
            const IconBadge(Icons.workspace_premium_outlined,
                bg: AppColors.red050, fg: AppColors.red, size: 48),
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
                        color: AppColors.red,
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

  Widget _servicesGrid(List<ServiceModel> services) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: services.length,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.2,
        ),
        itemBuilder: (_, i) {
          final s = services[i];
          return GestureDetector(
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => BookingScreen(service: s)),
            ),
            child: SoftCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  IconBadge(s.icon, size: 40),
                  const Spacer(),
                  Text(s.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 13)),
                  Text(formatAmount(s.priceSar),
                      style: const TextStyle(
                          color: AppColors.red,
                          fontWeight: FontWeight.w800,
                          fontSize: 13)),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _features(List<LandingFeatureModel> features) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18),
      child: SoftCard(
        child: Column(
          children: features
              .map((f) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const IconBadge(Icons.check, size: 32),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(f.titleAr,
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w800,
                                      fontSize: 14)),
                              Text(f.descriptionAr,
                                  style: const TextStyle(
                                      color: AppColors.ink500,
                                      fontSize: 12)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ))
              .toList(),
        ),
      ),
    );
  }
}
