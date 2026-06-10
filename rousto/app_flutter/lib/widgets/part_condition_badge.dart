import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// شارة حالة القطعة (جديد / مستعمل) على بطاقة المنتج.
class PartConditionBadge extends StatelessWidget {
  final bool isUsed;
  final bool compact;

  const PartConditionBadge({
    super.key,
    required this.isUsed,
    this.compact = true,
  });

  @override
  Widget build(BuildContext context) {
    final label = isUsed ? 'مستعمل' : 'جديد';
    final bg = isUsed ? AppColors.navy : AppColors.navy050;
    final fg = isUsed ? Colors.white : AppColors.navy;
    final padding = compact
        ? const EdgeInsets.symmetric(horizontal: 8, vertical: 3)
        : const EdgeInsets.symmetric(horizontal: 10, vertical: 4);

    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
        boxShadow: isUsed
            ? [
                BoxShadow(
                  color: AppColors.navy.withValues(alpha: 0.25),
                  blurRadius: 4,
                  offset: const Offset(0, 1),
                ),
              ]
            : null,
      ),
      child: Text(
        label,
        style: TextStyle(
          color: fg,
          fontSize: compact ? 10 : 11,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }
}
