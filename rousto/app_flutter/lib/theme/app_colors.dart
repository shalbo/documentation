import 'package:flutter/material.dart';

/// ألوان روستو مستوحاة من الشعار: أحمر #D31E28 · كحلي #0B2C44 · أسود.
class AppColors {
  AppColors._();

  // Logo red
  static const Color red = Color(0xFFD31E28);
  static const Color red600 = Color(0xFFB81922);
  static const Color red700 = Color(0xFF9A151C);
  static const Color red800 = Color(0xFF7A1016);
  static const Color red050 = Color(0xFF2D1518);

  // Logo navy
  static const Color navy = Color(0xFF0B2C44);
  static const Color navyLight = Color(0xFF123A5C);

  // Dark surfaces
  static const Color ink900 = Color(0xFFF5F6F8);
  static const Color ink700 = Color(0xFFD0D8E0);
  static const Color ink500 = Color(0xFF8FA3B3);
  static const Color ink300 = Color(0xFF5C7080);
  static const Color line = Color(0xFF1A3D5C);
  static const Color bg = Color(0xFF000000);
  static const Color surface = Color(0xFF0B2C44);
  static const Color cream = Color(0xFF0E3248);

  // Accents
  static const Color gold = Color(0xFFF2B705);
  static const Color green = Color(0xFF1E9E6A);

  // Gradients
  static const LinearGradient redGradient = LinearGradient(
    colors: [Color(0xFFD31E28), Color(0xFF9A151C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient darkGradient = LinearGradient(
    colors: [Color(0xFF000000), Color(0xFF0B2C44)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient navyGradient = LinearGradient(
    colors: [Color(0xFF0B2C44), Color(0xFF123A5C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
