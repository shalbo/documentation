import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../state/app_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'settings_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

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

        final user = state.user;
        final mon = state.monetization;
        final serviceCount = user?.servicesCount ?? 0;
        final vehicleCount = user?.vehiclesCount ?? 0;

        final items = <_ProfileItem>[
          _ProfileItem(
            Icons.directions_car_filled_outlined,
            l10n.myVehicles,
            l10n.vehicleCount(vehicleCount),
          ),
          _ProfileItem(
            Icons.receipt_long_outlined,
            l10n.orderHistory,
            l10n.previousServicesCount(serviceCount),
          ),
          _ProfileItem(
            Icons.credit_card,
            l10n.paymentMethods,
            l10n.paymentMethodsSubtitle,
          ),
          _ProfileItem(
            Icons.location_on_outlined,
            l10n.addresses,
            l10n.addressesSubtitle,
          ),
          _ProfileItem(
            Icons.card_giftcard_outlined,
            l10n.rewards,
            l10n.loyaltyPointsAvailable(state.loyaltyPoints),
          ),
          _ProfileItem(
            Icons.settings_outlined,
            l10n.settings,
            l10n.settingsSubtitle,
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const SettingsScreen()),
            ),
          ),
          _ProfileItem(
            Icons.support_agent_outlined,
            l10n.supportAndSafety,
            l10n.supportSubtitle,
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
                          user?.avatarInitials ?? l10n.unknownInitial,
                          style: const TextStyle(
                              color: AppColors.red600,
                              fontSize: 26,
                              fontWeight: FontWeight.w800),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        user?.fullName ?? l10n.guest,
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
                            l10n.membership(mon.planNameAr) +
                                (mon.discountPercent > 0
                                    ? l10n.membershipDiscount(
                                        mon.discountPercent)
                                    : ''),
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
                        _Stat(
                          '${user?.servicesCount ?? 0}',
                          serviceCount == 1
                              ? l10n.serviceStat
                              : l10n.servicesStat,
                        ),
                        _Stat(
                          '${user?.vehiclesCount ?? 0}',
                          vehicleCount == 1
                              ? l10n.vehicleStat
                              : l10n.vehiclesStat,
                        ),
                        _Stat('${state.loyaltyPoints}', l10n.pointsStat),
                        _Stat(
                          '${mon?.lifetimeSavingsSar.round() ?? 0}',
                          l10n.savingsStat,
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
                          onTap: it.onTap,
                          borderRadius: BorderRadius.circular(16),
                          child: Row(
                            children: [
                              IconBadge(it.icon, size: 40),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(it.title,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.w800,
                                            fontSize: 14)),
                                    Text(it.subtitle,
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

class _ProfileItem {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  const _ProfileItem(this.icon, this.title, this.subtitle, {this.onTap});
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
