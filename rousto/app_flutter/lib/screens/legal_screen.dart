import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';

enum LegalDocType { privacy, terms, warranty }

class LegalScreen extends StatelessWidget {
  final LegalDocType docType;

  const LegalScreen({super.key, required this.docType});

  String _title(AppLocalizations l10n) {
    switch (docType) {
      case LegalDocType.privacy:
        return l10n.privacyPolicy;
      case LegalDocType.terms:
        return l10n.termsOfService;
      case LegalDocType.warranty:
        return l10n.warrantyPolicy;
    }
  }

  String _content(AppLocalizations l10n, bool isArabic) {
    switch (docType) {
      case LegalDocType.privacy:
        return isArabic ? l10n.privacyContentAr : l10n.privacyContent;
      case LegalDocType.terms:
        return isArabic ? l10n.termsContentAr : l10n.termsContent;
      case LegalDocType.warranty:
        return isArabic ? l10n.warrantyContentAr : l10n.warrantyContent;
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: AppColors.bg,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        title: Text(_title(l10n),
            style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Text(
          _content(l10n, isArabic),
          style: const TextStyle(
            color: AppColors.ink700,
            fontSize: 14,
            height: 1.7,
          ),
        ),
      ),
    );
  }
}
