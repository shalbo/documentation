import 'package:flutter/material.dart';

/// هوية Rousto الرسمية — مستوحاة من شعار col.png
class AppColors {
  AppColors._();

  // Primary action / accent — brand-red (#C1121F)
  static const Color red = Color(0xFFC1121F);
  static const Color red600 = Color(0xFF9A0E18);
  static const Color red700 = Color(0xFF7A0B13);
  static const Color red050 = Color(0xFFFCE8EA);

  // Structural / dominant — brand-navy (#003049)
  static const Color navy = Color(0xFF003049);
  static const Color navyLight = Color(0xFF1A5578);
  static const Color navy050 = Color(0xFFE8EEF2);

  // System backgrounds
  static const Color ink900 = Color(0xFF003049);
  static const Color ink700 = Color(0xFF1A3D52);
  static const Color ink500 = Color(0xFF5B6B75);
  static const Color ink300 = Color(0xFF9AA8B2);
  static const Color line = Color(0xFFE8ECF0);
  static const Color bg = Color(0xFFF8F9FA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cream = Color(0xFFF8F9FA);

  // Accents
  static const Color gold = Color(0xFFF2B705);
  static const Color green = Color(0xFF2D9F6F);
  static const Color green050 = Color(0xFFE8F6EF);

  static const LinearGradient redGradient = LinearGradient(
    colors: [Color(0xFFC1121F), Color(0xFF9A0E18)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient navyGradient = LinearGradient(
    colors: [Color(0xFF003049), Color(0xFF1A5578)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient darkGradient = LinearGradient(
    colors: [Color(0xFF003049), Color(0xFF1A5578)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
