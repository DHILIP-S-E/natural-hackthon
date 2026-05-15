import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../widgets/tempo/gradient_orb.dart';

class TempoVoicePage extends StatefulWidget {
  const TempoVoicePage({super.key});

  @override
  State<TempoVoicePage> createState() => _TempoVoicePageState();
}

class _TempoVoicePageState extends State<TempoVoicePage> {
  bool _isMuted = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            _TopActions(),
            Expanded(
              child: Center(
                child: GradientOrb(size: 180, isListening: !_isMuted),
              ),
            ),
            _BottomControls(
              isMuted: _isMuted,
              onClose: () => context.pop(),
              onReset: () {},
              onMuteToggle: () => setState(() => _isMuted = !_isMuted),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

class _TopActions extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          _OutlineIconBtn(icon: Icons.volume_up_outlined, onTap: () {}),
          const SizedBox(width: 12),
          _OutlineIconBtn(icon: Icons.ios_share_outlined, onTap: () {}),
          const SizedBox(width: 12),
          _OutlineIconBtn(icon: Icons.warning_amber_outlined, onTap: () {}),
        ],
      ),
    );
  }
}

class _OutlineIconBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _OutlineIconBtn({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: const Color(0xFFE0D8F0), width: 1.5),
        ),
        child: Icon(icon, size: 18, color: const Color(0xFF666680)),
      ),
    );
  }
}

class _BottomControls extends StatelessWidget {
  final bool isMuted;
  final VoidCallback onClose;
  final VoidCallback onReset;
  final VoidCallback onMuteToggle;

  const _BottomControls({
    required this.isMuted,
    required this.onClose,
    required this.onReset,
    required this.onMuteToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _CircleControl(
          icon: Icons.close_rounded,
          onTap: onClose,
          color: const Color(0xFFF0EAFF),
          iconColor: const Color(0xFF7C3AED),
        ),
        const SizedBox(width: 24),
        _CircleControl(
          icon: Icons.refresh_rounded,
          onTap: onReset,
          color: const Color(0xFFF0EAFF),
          iconColor: const Color(0xFF7C3AED),
        ),
        const SizedBox(width: 24),
        _CircleControl(
          icon: isMuted ? Icons.mic_off_rounded : Icons.mic_none_rounded,
          onTap: onMuteToggle,
          color: isMuted ? const Color(0xFFFFE8E8) : const Color(0xFFF0EAFF),
          iconColor: isMuted ? Colors.red : const Color(0xFF7C3AED),
        ),
      ],
    );
  }
}

class _CircleControl extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final Color color;
  final Color iconColor;

  const _CircleControl({
    required this.icon,
    required this.onTap,
    required this.color,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 60,
        height: 60,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color),
        child: Icon(icon, color: iconColor, size: 26),
      ),
    );
  }
}
