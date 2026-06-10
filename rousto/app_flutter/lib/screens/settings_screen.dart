import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../state/locale_state.dart';
import '../theme/app_colors.dart';
import '../widgets/common.dart';
import 'legal_screen.dart';
import 'notifications_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final localeState = context.watch<LocaleState>();
    final currentCode = localeState.locale?.languageCode ?? 'ar';

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: Text(l10n.settings,
            style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(18, 8, 18, 24),
        children: [
          Text(l10n.language,
              style:
                  const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
          const SizedBox(height: 10),
          SoftCard(
            child: Column(
              children: [
                _LanguageTile(
                  label: l10n.arabic,
                  locale: const Locale('ar'),
                  selected: currentCode == 'ar',
                ),
                const Divider(height: 1),
                _LanguageTile(
                  label: l10n.english,
                  locale: const Locale('en'),
                  selected: currentCode == 'en',
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Text(l10n.notifications,
              style:
                  const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
          const SizedBox(height: 10),
          SoftCard(
            child: InkWell(
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const NotificationsScreen()),
              ),
              borderRadius: BorderRadius.circular(16),
              child: Row(
                children: [
                  const IconBadge(Icons.notifications_outlined, size: 40),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(l10n.notificationPreferences,
                        style: const TextStyle(
                            fontWeight: FontWeight.w800, fontSize: 14)),
                  ),
                  const Icon(Icons.chevron_left, color: AppColors.ink300),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          Text(l10n.legal,
              style:
                  const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
          const SizedBox(height: 10),
          SoftCard(
            child: Column(
              children: [
                _LegalLink(
                  title: l10n.privacyPolicy,
                  docType: LegalDocType.privacy,
                ),
                const Divider(height: 1),
                _LegalLink(
                  title: l10n.termsOfService,
                  docType: LegalDocType.terms,
                ),
                const Divider(height: 1),
                _LegalLink(
                  title: l10n.warrantyPolicy,
                  docType: LegalDocType.warranty,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LanguageTile extends StatelessWidget {
  final String label;
  final Locale locale;
  final bool selected;

  const _LanguageTile({
    required this.label,
    required this.locale,
    required this.selected,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
      trailing: selected
          ? const Icon(Icons.check_circle, color: AppColors.red600)
          : null,
      onTap: selected
          ? null
          : () => context.read<LocaleState>().setLocale(locale),
    );
  }
}

class _LegalLink extends StatelessWidget {
  final String title;
  final LegalDocType docType;

  const _LegalLink({required this.title, required this.docType});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
      trailing: const Icon(Icons.chevron_left, color: AppColors.ink300),
      onTap: () => Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => LegalScreen(docType: docType),
        ),
      ),
    );
  }
}
