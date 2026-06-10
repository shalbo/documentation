import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../theme/app_colors.dart';
import '../theme/app_decorations.dart';

/// شارة صغيرة (eyebrow) بخلفية حمراء فاتحة.
class Eyebrow extends StatelessWidget {
  final String text;
  final Color? bg;
  final Color? fg;
  const Eyebrow(this.text, {super.key, this.bg, this.fg});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bg ?? AppColors.red050,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: fg ?? AppColors.red600,
          fontWeight: FontWeight.w800,
          fontSize: 12,
          letterSpacing: 1,
        ),
      ),
    );
  }
}

/// أيقونة داخل مربّع ملوّن.
class IconBadge extends StatelessWidget {
  final IconData icon;
  final Color bg;
  final Color fg;
  final double size;
  const IconBadge(
    this.icon, {
    super.key,
    this.bg = AppColors.red050,
    this.fg = AppColors.red600,
    this.size = 44,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(size * 0.28),
      ),
      child: Icon(icon, color: fg, size: size * 0.5),
    );
  }
}

/// بطاقة بيضاء بظل ناعم.
class SoftCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color color;
  final bool featured;
  const SoftCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(14),
    this.color = AppColors.surface,
    this.featured = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: color,
        borderRadius: AppDecorations.borderRadius,
        border: Border.all(
          color: featured ? AppColors.red : AppColors.line,
          width: featured ? 1.2 : 0.8,
        ),
        boxShadow: featured
            ? AppDecorations.elevatedShadow
            : AppDecorations.cardShadow,
      ),
      child: child,
    );
  }
}

/// زر أساسي بتدرّج أحمر.
class GradientButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final Gradient gradient;
  final IconData? icon;
  const GradientButton({
    super.key,
    required this.label,
    this.onPressed,
    this.gradient = AppColors.redGradient,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onPressed,
        child: Ink(
          decoration: BoxDecoration(
            gradient: gradient,
            borderRadius: BorderRadius.circular(14),
            boxShadow: [
              BoxShadow(
                color: AppColors.red.withValues(alpha: 0.30),
                blurRadius: 22,
                offset: const Offset(0, 12),
              ),
            ],
          ),
          child: Container(
            height: 52,
            alignment: Alignment.center,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                  ),
                ),
                if (icon != null) ...[
                  const SizedBox(width: 8),
                  Icon(icon, color: Colors.white, size: 20),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// شارة وضع تجريبي عند فشل الاتصال بالـ API.
class DemoBadge extends StatelessWidget {
  const DemoBadge({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF3D6),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        l10n.demoMode,
        style: const TextStyle(
          color: Color(0xFFB07D00),
          fontWeight: FontWeight.w700,
          fontSize: 11,
        ),
      ),
    );
  }
}

/// عنوان قسم بسيط مع زر "عرض الكل".
class RowHeader extends StatelessWidget {
  final String title;
  final String? action;
  final VoidCallback? onAction;
  const RowHeader(this.title, {super.key, this.action, this.onAction});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title,
            style:
                const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
        if (action != null)
          GestureDetector(
            onTap: onAction,
            child: Text(action!,
                style: const TextStyle(
                    color: AppColors.red600,
                    fontWeight: FontWeight.w700,
                    fontSize: 13)),
          ),
      ],
    );
  }
}
