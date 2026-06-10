import 'package:flutter/material.dart';

/// ألوان روستو: أحمر وكحلي من الشعار · خلفية بيضاء مريحة.
class AppColors {
  AppColors._();

  // Logo red
  static const Color red = Color(0xFFD31E28);
  static const Color red600 = Color(0xFFB81922);
  static const Color red700 = Color(0xFF9A151C);
  static const Color red800 = Color(0xFF7A1016);
  static const Color red050 = Color(0xFFFDECEC);

  // Logo navy (للعناوين والتمييز)
  static const Color navy = Color(0xFF0B2C44);
  static const Color navyLight = Color(0xFF123A5C);

  // Light neutrals
  static const Color ink900 = Color(0xFF15161A);
  static const Color ink700 = Color(0xFF2B2D34);
  static const Color ink500 = Color(0xFF5B5E66);
  static const Color ink300 = Color(0xFF9A9DA6);
  static const Color line = Color(0xFFE4E2DD);
  static const Color bg = Color(0xFFFFFFFF);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cream = Color(0xFFF8F7F4);

  // Accents
  static const Color gold = Color(0xFFF2B705);
  static const Color green = Color(0xFF1E9E6A);

  // Gradients
  static const LinearGradient redGradient = LinearGradient(
    colors: [Color(0xFFD31E28), Color(0xFF9A151C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient navyGradient = LinearGradient(
    colors: [Color(0xFF0B2C44), Color(0xFF123A5C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  /// للبطاقات الترويجية الداكنة فقط.
  static const LinearGradient darkGradient = LinearGradient(
    colors: [Color(0xFF0B2C44), Color(0xFF123A5C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
