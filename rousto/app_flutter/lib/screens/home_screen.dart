import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';

import '../currency.dart';
import '../data/models.dart';
import '../l10n/app_localizations.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'ai_scan_screen.dart';
import 'booking_screen.dart';
import 'pricing_screen.dart';
import 'tracking_screen.dart';

class HomeScreen extends StatelessWidget {
  final VoidCallback onBook;
  const HomeScreen({super.key, required this.onBook});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, state, _) {
        if (state.loading) {
          return const Center(child: CircularProgressIndicator());
        }

        return RefreshIndicator(
          onRefresh: state.load,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.only(bottom: 110),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _header(context, state),
                if (state.activeBooking != null)
                  Transform.translate(
                    offset: const Offset(0, -16),
                    child: _activeServiceCard(
                        context, state.activeBooking!, state),
                  ),
                Padding(
                  padding: EdgeInsets.fromLTRB(
                    18,
                    state.activeBooking != null ? 4 : 0,
                    18,
                    0,
                  ),
                  child: _categories(state),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 16, 18, 0),
                  child: RowHeader(
                    AppLocalizations.of(context)!.popularServices,
                    action: AppLocalizations.of(context)!.viewAll,
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: _servicesGrid(context, state.currentServices),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 18, 18, 0),
                  child: _pricingTeaser(context),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: _aiScanCard(context),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: _promo(context, state),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _header(BuildContext context, AppState state) {
    final l10n = AppLocalizations.of(context)!;
    final user = state.user;
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 0, 18, 30),
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
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    SvgPicture.asset('assets/logo.svg', height: 28),
                    const SizedBox(width: 8),
                    Text(l10n.appTitle,
                        style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w800,
                            fontSize: 18)),
                  ],
                ),
                Row(
                  children: [
                    if (state.usingMockData) const DemoBadge(),
                    if (state.usingMockData) const SizedBox(width: 8),
                    CircleAvatar(
                      radius: 19,
                      backgroundColor: Colors.white24,
                      child: Text(
                        user?.avatarInitials ?? l10n.unknownInitial,
                        style: const TextStyle(
                            color: Colors.white, fontWeight: FontWeight.w800),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(l10n.welcomeBack,
                style: const TextStyle(color: Color(0xFFE8C4C6), fontSize: 13)),
            Text(
              user?.fullName ?? l10n.guest,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Row(
                children: [
                  const Icon(Icons.search, color: Colors.white, size: 20),
                  const SizedBox(width: 8),
                  Text(l10n.searchService,
                      style: const TextStyle(color: Color(0xFFE8D0D2))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _activeServiceCard(
      BuildContext context, BookingModel booking, AppState state) {
    final l10n = AppLocalizations.of(context)!;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 18),
      child: GestureDetector(
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => TrackingScreen(bookingId: booking.id),
          ),
        ),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppColors.line),
            boxShadow: const [
              BoxShadow(
                color: Color(0x0F15161A),
                blurRadius: 14,
                offset: Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              IconBadge(
                iconFromKey(booking.serviceIconKey),
                bg: AppColors.red050,
                fg: AppColors.red,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l10n.activeService,
                        style: const TextStyle(
                            color: AppColors.ink900,
                            fontWeight: FontWeight.w800)),
                    Text(
                      l10n.bookingStatusLine(
                        booking.serviceName ?? l10n.service,
                        booking.statusLabelAr,
                      ),
                      style: const TextStyle(
                          color: AppColors.ink500, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const CircleAvatar(
                radius: 15,
                backgroundColor: AppColors.red050,
                child: Icon(Icons.arrow_back,
                    size: 16, color: AppColors.red600),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _categories(AppState state) {
    return SizedBox(
      height: 38,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: state.categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          final active = i == state.categoryIndex;
          return GestureDetector(
            onTap: () => state.selectCategory(i),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: active ? AppColors.red050 : AppColors.cream,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(
                    color: active ? AppColors.red : AppColors.line),
              ),
              child: Text(
                state.categories[i].nameAr,
                style: TextStyle(
                  color: active ? AppColors.red600 : AppColors.ink700,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _servicesGrid(BuildContext context, List<ServiceModel> services) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: services.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.25,
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
                        fontWeight: FontWeight.w800, fontSize: 14)),
                Text(s.duration,
                    style: const TextStyle(
                        color: AppColors.ink300, fontSize: 11)),
                const SizedBox(height: 4),
                Text(formatAmount(s.price),
                    style: const TextStyle(
                        color: AppColors.red600,
                        fontWeight: FontWeight.w800,
                        fontSize: 13)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _pricingTeaser(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return GestureDetector(
      onTap: () => Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const PricingScreen()),
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.cream,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.line),
        ),
        child: Row(
          children: [
            const IconBadge(Icons.sell_outlined,
                bg: AppColors.red050, fg: AppColors.red, size: 48),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l10n.pricingPlans,
                      style: const TextStyle(
                          color: AppColors.ink900,
                          fontWeight: FontWeight.w800,
                          fontSize: 15)),
                  Text(l10n.pricingPlansSubtitle,
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

  Widget _aiScanCard(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return GestureDetector(
      onTap: () => Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => const AiScanScreen()),
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.line),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0F15161A),
              blurRadius: 12,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            const IconBadge(Icons.document_scanner_outlined, size: 48),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l10n.photoScan,
                      style: const TextStyle(
                          fontWeight: FontWeight.w800, fontSize: 15)),
                  Text(l10n.photoScanSubtitle,
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

  Widget _promo(BuildContext context, AppState state) {
    final l10n = AppLocalizations.of(context)!;
    final promo = state.promotions.isNotEmpty ? state.promotions.first : null;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppColors.darkGradient,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  promo?.title ?? l10n.firstBookingDiscount,
                  style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                      fontSize: 15),
                ),
                Text(
                  promo != null
                      ? l10n.useCode(promo.code)
                      : l10n.useCode('ROUSTO'),
                  style: const TextStyle(
                      color: Color(0xFFC7C8CF), fontSize: 12),
                ),
              ],
            ),
          ),
          Text(l10n.promoPercent,
              style: const TextStyle(
                  color: AppColors.red,
                  fontSize: 30,
                  fontWeight: FontWeight.w800)),
        ],
      ),
    );
  }
}
