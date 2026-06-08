import 'package:flutter/material.dart';

/// ألوان روستو مستوحاة مباشرة من الشعار.
class AppColors {
  AppColors._();

  // Brand red
  static const Color red = Color(0xFFE11B22);
  static const Color red600 = Color(0xFFC2161C);
  static const Color red700 = Color(0xFFA3141A);
  static const Color red800 = Color(0xFF7A0F14);
  static const Color red050 = Color(0xFFFDECEC);

  // Neutrals
  static const Color ink900 = Color(0xFF15161A);
  static const Color ink700 = Color(0xFF2B2D34);
  static const Color ink500 = Color(0xFF5B5E66);
  static const Color ink300 = Color(0xFF9A9DA6);
  static const Color line = Color(0xFFE4E2DD);
  static const Color bg = Color(0xFFF2F1ED);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cream = Color(0xFFF8F7F4);

  // Accents
  static const Color gold = Color(0xFFF2B705);
  static const Color green = Color(0xFF1E9E6A);

  // Gradients
  static const LinearGradient redGradient = LinearGradient(
    colors: [Color(0xFFE11B22), Color(0xFFA3141A)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient darkGradient = LinearGradient(
    colors: [Color(0xFF1D1E24), Color(0xFF2B2D34)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
