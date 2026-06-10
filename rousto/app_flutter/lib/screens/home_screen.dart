import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';

import '../currency.dart';
import '../data/models.dart';
import '../l10n/app_localizations.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../theme/app_decorations.dart';
import '../widgets/common.dart';
import '../widgets/vehicle_selector.dart';
import 'booking_screen.dart';
import 'catalog_screen.dart';
import 'parts_screen.dart';
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
                    child: _activeOrderCard(
                        context, state.activeBooking!, state),
                  ),
                Padding(
                  padding: EdgeInsets.fromLTRB(
                    18,
                    state.activeBooking != null ? 4 : 0,
                    18,
                    0,
                  ),
                  child: _partCategories(state),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: GestureDetector(
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const CatalogScreen()),
                    ),
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: AppDecorations.card(),
                      child: const Row(
                        children: [
                          Icon(Icons.grid_view_rounded, color: AppColors.navy),
                          SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('تصفح الكتالوج',
                                    style: TextStyle(
                                        fontWeight: FontWeight.w800,
                                        fontSize: 15)),
                                Text('أقسام رئيسية ← فرعية ← قطع متوافقة',
                                    style: TextStyle(
                                        color: AppColors.ink500,
                                        fontSize: 11)),
                              ],
                            ),
                          ),
                          Icon(Icons.chevron_left, color: AppColors.ink300),
                        ],
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 16, 18, 0),
                  child: RowHeader('قطع مميزة', action: 'عرض الكل'),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: _partsGrid(context, state),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 18, 18, 0),
                  child: RowHeader('محلات موثوقة', action: 'المزيد'),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: _vendorsRow(state),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 12, 18, 0),
                  child: _servicesBanner(context, onBook),
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
        gradient: AppColors.navyGradient,
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(20)),
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
                    const Text('سوق قطع الغيار',
                        style: TextStyle(
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
            const SizedBox(height: 12),
            VehicleSelector(
              onChanged: (sel) => state.setFitment(sel),
            ),
            const SizedBox(height: 12),
            if (state.fitment?.isComplete == true)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  'عرض القطع المتوافقة مع: ${state.fitment!.label}',
                  style: const TextStyle(color: Color(0xFFE8D0D2), fontSize: 11),
                ),
              ),
            GestureDetector(
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => PartsScreen(
                    initialCarYearId: state.fitment?.carYearId,
                    openVinMode: false,
                  ),
                ),
              ),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.16),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.search, color: Colors.white, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'ابحث برقم القطعة OEM أو ماركة السيارة…',
                        style: TextStyle(color: Color(0xFFE8D0D2)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton.icon(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => PartsScreen(
                      initialCarYearId: state.fitment?.carYearId,
                      openVinMode: true,
                    ),
                  ),
                ),
                icon: const Icon(Icons.qr_code_scanner, size: 18),
                label: const Text('البحث برقم الهيكل (VIN)'),
                style: TextButton.styleFrom(foregroundColor: Colors.white70),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _activeOrderCard(
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
            borderRadius: AppDecorations.borderRadius,
            border: Border.all(color: AppColors.line),
            boxShadow: AppDecorations.cardShadow,
          ),
          child: Row(
            children: [
              const IconBadge(
                Icons.local_shipping_outlined,
                bg: AppColors.red050,
                fg: AppColors.red,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('طلبك قيد التنفيذ',
                        style: TextStyle(
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

  Widget _partCategories(AppState state) {
    final categories = state.partCategories;
    if (categories.isEmpty) return const SizedBox.shrink();

    return SizedBox(
      height: 38,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          final active = i == state.partCategoryIndex;
          return GestureDetector(
            onTap: () => state.selectPartCategory(i),
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
                categories[i].nameAr,
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

  Widget _partsGrid(BuildContext context, AppState state) {
    final parts = state.visibleParts.isNotEmpty
        ? state.visibleParts
        : (state.marketplace?.featuredParts ?? []);

    if (parts.isEmpty) {
      return const SoftCard(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('لا توجد قطع في هذا التصنيف حالياً',
              style: TextStyle(color: AppColors.ink500)),
        ),
      );
    }

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: parts.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.92,
      ),
      itemBuilder: (_, i) {
        final p = parts[i];
        return GestureDetector(
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute(builder: (_) => const PartsScreen()),
          ),
          child: SoftCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IconBadge(
                  _iconForCategory(p.categorySlug),
                  size: 40,
                ),
                if (p.isOem)
                  Container(
                    margin: const EdgeInsets.only(top: 6),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.red050,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Text('OEM',
                        style: TextStyle(
                            color: AppColors.red600,
                            fontSize: 10,
                            fontWeight: FontWeight.w800)),
                  ),
                const Spacer(),
                Text(p.nameAr,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 13)),
                Text(p.partNumber,
                    style: const TextStyle(
                        color: AppColors.ink300, fontSize: 10)),
                const SizedBox(height: 4),
                Text(formatAmount(p.priceSar),
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

  IconData _iconForCategory(String? slug) {
    switch (slug) {
      case 'filters':
        return Icons.filter_alt_outlined;
      case 'brakes':
        return Icons.disc_full_outlined;
      case 'electrical':
        return Icons.electric_bolt_outlined;
      case 'belts':
        return Icons.settings_suggest_outlined;
      case 'engines':
        return Icons.precision_manufacturing_outlined;
      default:
        return Icons.build_circle_outlined;
    }
  }

  Widget _vendorsRow(AppState state) {
    final vendors = state.featuredVendors;
    if (vendors.isEmpty) return const SizedBox.shrink();

    return SizedBox(
      height: 96,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: vendors.length,
        separatorBuilder: (_, __) => const SizedBox(width: 10),
        itemBuilder: (_, i) {
          final v = vendors[i];
          return Container(
            width: 200,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.line),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.storefront_outlined,
                    color: AppColors.red, size: 22),
                const SizedBox(height: 8),
                Text(v.businessName,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        fontWeight: FontWeight.w800, fontSize: 13)),
                Text(v.city,
                    style: const TextStyle(
                        color: AppColors.ink500, fontSize: 11)),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _servicesBanner(BuildContext context, VoidCallback onBook) {
    return GestureDetector(
      onTap: onBook,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.cream,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.line),
        ),
        child: Row(
          children: [
            const IconBadge(Icons.handyman_outlined,
                bg: AppColors.red050, fg: AppColors.red, size: 48),
            const SizedBox(width: 12),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('صيانة وسطحات',
                      style: TextStyle(
                          color: AppColors.ink900,
                          fontWeight: FontWeight.w800,
                          fontSize: 15)),
                  Text('حجز ورشة أو طلب ساحبة — خدمة مكمّلة',
                      style: TextStyle(color: AppColors.ink500, fontSize: 12)),
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
