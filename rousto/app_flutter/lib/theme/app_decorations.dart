import 'package:flutter/material.dart';

import 'app_colors.dart';

/// ظلال ناعمة وضبابية — هوية Rousto من col.png
class AppDecorations {
  AppDecorations._();

  static const double radius = 14;

  static BorderRadius get borderRadius => BorderRadius.circular(radius);

  static List<BoxShadow> get cardShadow => const [
        BoxShadow(
          color: Color(0x0A003049),
          blurRadius: 20,
          offset: Offset(0, 6),
          spreadRadius: 0,
        ),
      ];

  static List<BoxShadow> get elevatedShadow => const [
        BoxShadow(
          color: Color(0x14003049),
          blurRadius: 24,
          offset: Offset(0, 10),
        ),
      ];

  static BoxDecoration card({Color? color, bool featured = false}) {
    return BoxDecoration(
      color: color ?? AppColors.surface,
      borderRadius: borderRadius,
      border: Border.all(
        color: featured ? AppColors.red.withValues(alpha: 0.25) : AppColors.line,
        width: featured ? 1.2 : 0.8,
      ),
      boxShadow: featured ? elevatedShadow : cardShadow,
    );
  }

  static BoxDecoration vinMatchBadge({bool matched = true}) {
    return BoxDecoration(
      color: matched ? AppColors.green050 : AppColors.navy050,
      borderRadius: borderRadius,
      border: Border.all(
        color: matched
            ? AppColors.green.withValues(alpha: 0.35)
            : AppColors.navy.withValues(alpha: 0.2),
      ),
      boxShadow: cardShadow,
    );
  }
}
