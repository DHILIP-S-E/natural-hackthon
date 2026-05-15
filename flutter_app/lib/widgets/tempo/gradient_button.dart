import 'package:flutter/material.dart';
import '../../config/app_colors.dart';

class GradientIconButton extends StatelessWidget {
  final IconData icon;
  final double size;
  final VoidCallback? onTap;
  final Gradient gradient;

  const GradientIconButton({
    super.key,
    required this.icon,
    this.size = 56,
    this.onTap,
    this.gradient = AppColors.primaryGradient,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(shape: BoxShape.circle, gradient: gradient),
        child: Icon(icon, color: Colors.white, size: size * 0.44),
      ),
    );
  }
}

class GradientSendButton extends StatelessWidget {
  final VoidCallback? onTap;

  const GradientSendButton({super.key, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          gradient: AppColors.primaryGradient,
        ),
        child: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
      ),
    );
  }
}
