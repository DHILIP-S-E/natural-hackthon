import 'package:flutter/material.dart';

class AppColors {
  static const Color primary = Color(0xFF7C3AED);
  static const Color primaryLight = Color(0xFFAB7FF5);
  static const Color primarySurface = Color(0xFFF3EEFF);

  static const Color userBubble = Color(0xFF7C3AED);
  static const Color aiBubble = Color(0xFFFFFFFF);
  static const Color aiBubbleBorder = Color(0xFFEEE6FF);

  static const Color scaffoldBg = Color(0xFFFAF7FF);
  static const Color chipBg = Color(0xFFF3EEFF);

  static const Color streakOrange = Color(0xFFFF9500);
  static const Color navSelected = Color(0xFF7C3AED);
  static const Color navUnselected = Color(0xFFB0A8C0);

  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF7C3AED), Color(0xFFB06EF5)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient orbGradient = LinearGradient(
    colors: [Color(0xFF7C3AED), Color(0xFFE040FB), Color(0xFFAB7FF5)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient bgGradient = LinearGradient(
    colors: [Color(0xFFFFFFFF), Color(0xFFF0E6FF)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
