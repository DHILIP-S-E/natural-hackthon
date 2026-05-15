import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../config/app_colors.dart';

class GradientOrb extends StatefulWidget {
  final double size;
  final bool isListening;

  const GradientOrb({super.key, this.size = 180, this.isListening = false});

  @override
  State<GradientOrb> createState() => _GradientOrbState();
}

class _GradientOrbState extends State<GradientOrb>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _pulse;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat(reverse: true);

    _pulse = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulse,
      builder: (context, _) {
        return Transform.scale(
          scale: _pulse.value,
          child: Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const RadialGradient(
                center: Alignment(-0.3, -0.3),
                radius: 1.0,
                colors: [
                  Color(0xFFD070F0),
                  Color(0xFF8B3FF0),
                  Color(0xFF5B1ABF),
                ],
                stops: [0.0, 0.5, 1.0],
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.4),
                  blurRadius: 40,
                  spreadRadius: 8,
                ),
                BoxShadow(
                  color: const Color(0xFFE040FB).withOpacity(0.2),
                  blurRadius: 60,
                  spreadRadius: 16,
                ),
              ],
            ),
            child: CustomPaint(painter: _OrbHighlightPainter()),
          ),
        );
      },
    );
  }
}

class _OrbHighlightPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..shader = const RadialGradient(
        center: Alignment(-0.5, -0.5),
        radius: 0.6,
        colors: [Colors.white54, Colors.transparent],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    canvas.drawCircle(
      Offset(size.width * 0.35, size.height * 0.3),
      size.width * 0.28,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
