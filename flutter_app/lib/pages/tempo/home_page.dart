import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../providers/chat_provider.dart';
import '../../widgets/tempo/gradient_button.dart';
import '../beautrix/beautrix_live_page.dart';

class TempoHomePage extends ConsumerWidget {
  const TempoHomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.scaffoldBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.bgGradient),
        child: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _TopBar(),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 28),
                      const _AiGreetingCard(),
                      const SizedBox(height: 36),
                      const _ActionButtons(),
                      const SizedBox(height: 32),
                      const _ChatIdeasSection(),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
              const _BottomNav(),
            ],
          ),
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      child: Row(
        children: [
          const Icon(Icons.menu_rounded, size: 26, color: Color(0xFF1A1A2E)),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF3E0),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('🔥', style: TextStyle(fontSize: 16)),
                SizedBox(width: 6),
                Text(
                  '31 days streak',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                    color: Color(0xFF1A1A2E),
                  ),
                ),
              ],
            ),
          ),
          const Spacer(),
          Stack(
            clipBehavior: Clip.none,
            children: [
              const Icon(Icons.notifications_none_rounded, size: 26, color: Color(0xFF1A1A2E)),
              Positioned(
                top: -2,
                right: -2,
                child: Container(
                  width: 16,
                  height: 16,
                  decoration: const BoxDecoration(color: Colors.red, shape: BoxShape.circle),
                  child: const Center(
                    child: Text('3', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _AiGreetingCard extends StatelessWidget {
  const _AiGreetingCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.08),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            'TEMPO AI',
            style: TextStyle(
              fontWeight: FontWeight.w800,
              fontSize: 13,
              color: AppColors.primary,
              letterSpacing: 1.2,
            ),
          ),
          SizedBox(height: 12),
          Text(
            "Hello Araf,\nYou've not been lately drinking water\nproperly and missing out your habit.\n\nLet's get back on track!",
            style: TextStyle(fontSize: 15, color: Color(0xFF1A1A2E), height: 1.6),
          ),
        ],
      ),
    );
  }
}

class _ActionButtons extends StatelessWidget {
  const _ActionButtons();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        GradientIconButton(
          icon: Icons.chat_bubble_outline_rounded,
          size: 64,
          onTap: () => context.push('/tempo/chat'),
        ),
        const SizedBox(width: 16),
        GradientIconButton(
          icon: Icons.mic_none_rounded,
          size: 64,
          onTap: () => context.push('/tempo/voice'),
        ),
      ],
    );
  }
}

class _ChatIdeasSection extends StatelessWidget {
  const _ChatIdeasSection();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Chat ideas',
          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: Color(0xFF1A1A2E)),
        ),
        const SizedBox(height: 14),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: chatIdeas.map((idea) {
            return GestureDetector(
              onTap: () => context.push('/tempo/chat', extra: idea),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.chipBg,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  idea,
                  style: const TextStyle(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w500,
                    fontSize: 13,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class _BottomNav extends StatelessWidget {
  const _BottomNav();

  static const _items = [
    (icon: Icons.check_box_outlined, label: 'To-do'),
    (icon: Icons.bar_chart_rounded, label: 'Habits'),
    (icon: Icons.track_changes_rounded, label: 'Track'),
    (icon: Icons.person_outline_rounded, label: 'Profile'),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Color(0x0A000000), blurRadius: 12, offset: Offset(0, -2))],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: _items.asMap().entries.map((entry) {
          final i = entry.key;
          final item = entry.value;
          final isSelected = i == 0;
          final isCenter = i == 2;

          return GestureDetector(
            onTap: isCenter
                ? () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => const BeautrixLivePage(),
                        fullscreenDialog: true,
                      ),
                    )
                : () {},
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (isCenter)
                  Container(
                    width: 44,
                    height: 44,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: AppColors.primaryGradient,
                    ),
                    child: Icon(item.icon, color: Colors.white, size: 22),
                  )
                else
                  Icon(
                    item.icon,
                    color: isSelected ? AppColors.navSelected : AppColors.navUnselected,
                    size: 24,
                  ),
                const SizedBox(height: 4),
                Text(
                  item.label,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                    color: isSelected ? AppColors.navSelected : AppColors.navUnselected,
                  ),
                ),
                if (isSelected) ...[
                  const SizedBox(height: 3),
                  Container(
                    width: 4,
                    height: 4,
                    decoration: const BoxDecoration(color: AppColors.navSelected, shape: BoxShape.circle),
                  ),
                ],
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}
