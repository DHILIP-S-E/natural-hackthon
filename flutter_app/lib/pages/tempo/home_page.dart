import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;
import '../../config/app_colors.dart';
import '../../providers/user_provider.dart';
import '../beautrix/beautrix_live_page.dart';

class TempoHomePage extends ConsumerStatefulWidget {
  const TempoHomePage({super.key});

  @override
  ConsumerState<TempoHomePage> createState() => _TempoHomePageState();
}

class _TempoHomePageState extends ConsumerState<TempoHomePage> with SingleTickerProviderStateMixin {
  late AnimationController _orbCtrl;

  @override
  void initState() {
    super.initState();
    _orbCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _orbCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F), // Deep premium dark background
      body: Stack(
        children: [
          // Background ambient glow
          Positioned(
            top: -100,
            left: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    const Color(0xFFC9A96E).withOpacity(0.15),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),

          SafeArea(
            child: CustomScrollView(
              slivers: [
                const SliverToBoxAdapter(child: _PremiumHeader()),
                SliverToBoxAdapter(child: const SizedBox(height: 30)),
                
                // 1. Beautrix Live AI Hero
                SliverToBoxAdapter(
                  child: _HeroOrbSection(orbCtrl: _orbCtrl),
                ),
                
                SliverToBoxAdapter(child: const SizedBox(height: 40)),

                // 2. Current Appointment (Smart)
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: _SmartAppointmentCard(),
                  ),
                ),

                SliverToBoxAdapter(child: const SizedBox(height: 24)),

                // 3. Beauty Pass (Exclusive)
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: _BeautyPassCard(),
                  ),
                ),

                SliverToBoxAdapter(child: const SizedBox(height: 24)),

                // 4. Personalized Recommendation
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: _RecommendationCard(),
                  ),
                ),

                SliverToBoxAdapter(child: const SizedBox(height: 120)), // padding for bottom nav
              ],
            ),
          ),

          // Floating Bottom Nav
          const Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: _PremiumBottomNav(),
          ),
        ],
      ),
    );
  }
}

class _PremiumHeader extends ConsumerWidget {
  const _PremiumHeader();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userProvider);
    final name = userAsync.when(
      data: (u) => u.firstName,
      loading: () => "...",
      error: (_, __) => "Guest",
    );

    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'GOOD MORNING',
                style: TextStyle(
                  color: Color(0xFFC9A96E),
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 2.0,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                name,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontFamily: 'Playfair Display',
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white.withOpacity(0.1)),
            ),
            child: const Icon(Icons.person_outline, color: Colors.white, size: 20),
          )
        ],
      ),
    );
  }
}

class _HeroOrbSection extends StatelessWidget {
  final AnimationController orbCtrl;
  const _HeroOrbSection({required this.orbCtrl});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GestureDetector(
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => const BeautrixLivePage(),
              fullscreenDialog: true,
            ),
          ),
          child: AnimatedBuilder(
            animation: orbCtrl,
            builder: (context, child) {
              final scale = 1.0 + (0.05 * orbCtrl.value);
              final glowOpacity = 0.4 + (0.3 * orbCtrl.value);
              
              return Stack(
                alignment: Alignment.center,
                children: [
                  // Outer breathing glow
                  Container(
                    width: 180 * scale,
                    height: 180 * scale,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: RadialGradient(
                        colors: [
                          const Color(0xFFC9A96E).withOpacity(glowOpacity),
                          const Color(0xFFC9A96E).withOpacity(0.0),
                        ],
                      ),
                    ),
                  ),
                  // Inner solid orb
                  Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: const LinearGradient(
                        colors: [Color(0xFFE8D3A2), Color(0xFFC9A96E), Color(0xFF8B6914)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFC9A96E).withOpacity(0.5),
                          blurRadius: 30,
                          spreadRadius: 2,
                        )
                      ],
                    ),
                    child: const Icon(Icons.auto_awesome, color: Colors.white, size: 36),
                  ),
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          'BEAUTRIX LIVE AI',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: 3.0,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Tap to start live beauty consultation',
          style: TextStyle(
            color: Colors.white.withOpacity(0.5),
            fontSize: 12,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }
}

class _SmartAppointmentCard extends StatelessWidget {
  const _SmartAppointmentCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.03),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'UPCOMING APPOINTMENT',
                style: TextStyle(
                  color: Color(0xFFC9A96E),
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.5,
                ),
              ),
              Icon(Icons.arrow_forward_ios, color: Colors.white.withOpacity(0.3), size: 12),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Glow Studio • Today 4:30 PM',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontFamily: 'Playfair Display',
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Hydrating Facial + Hair Spa',
            style: TextStyle(
              color: Colors.white.withOpacity(0.6),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFC9A96E).withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFC9A96E).withOpacity(0.2)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.auto_awesome, color: Color(0xFFC9A96E), size: 16),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI Insight',
                        style: TextStyle(
                          color: Color(0xFFC9A96E),
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Arrive with clean, makeup-free skin to maximize the absorption of the hydrating serums.',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 12,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _BeautyPassCard extends StatelessWidget {
  const _BeautyPassCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF2A2A35), Color(0xFF1A1A24)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.4),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'BEAUTRIX GOLD',
                style: TextStyle(
                  color: Color(0xFFE8D3A2),
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 2.0,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Premium Member',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontFamily: 'Playfair Display',
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                '2 Luxury Sessions Remaining',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 13,
                ),
              ),
            ],
          ),
          GestureDetector(
            onTap: () => context.push('/tempo/pass'),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.1),
                borderRadius: BorderRadius.circular(30),
              ),
              child: const Text(
                'View Details',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          )
        ],
      ),
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  const _RecommendationCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.03),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.troubleshoot, color: Color(0xFFC9A96E), size: 16),
              const SizedBox(width: 8),
              const Text(
                'AI RECOMMENDATION',
                style: TextStyle(
                  color: Color(0xFFC9A96E),
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.5,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            'Keratin Restoration Protocol',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontFamily: 'Playfair Display',
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Based on your recent hair scan showing elevated porosity, this treatment will rebuild structural integrity.',
            style: TextStyle(
              color: Colors.white.withOpacity(0.6),
              fontSize: 13,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 20),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Center(
              child: Text(
                'Book Recommendation',
                style: TextStyle(
                  color: Color(0xFF0A0A0F),
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PremiumBottomNav extends StatelessWidget {
  const _PremiumBottomNav();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 90,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [
            const Color(0xFF0A0A0F),
            const Color(0xFF0A0A0F).withOpacity(0.8),
            Colors.transparent,
          ],
        ),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _NavItem(icon: Icons.calendar_today_outlined, label: 'Book', active: false, route: '/tempo/bookings'),
              _NavItem(icon: Icons.explore_outlined, label: 'Discover', active: true, route: '/tempo'),
              _NavItem(icon: Icons.person_outline, label: 'Profile', active: false, route: '/tempo/passport'),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool active;
  final String route;

  const _NavItem({required this.icon, required this.label, required this.active, required this.route});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        if (!active) {
          context.push(route);
        }
      },
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: active ? const Color(0xFFC9A96E) : Colors.white.withOpacity(0.3),
            size: 24,
          ),
          const SizedBox(height: 6),
          Text(
            label,
            style: TextStyle(
              color: active ? const Color(0xFFC9A96E) : Colors.white.withOpacity(0.3),
              fontSize: 10,
              fontWeight: active ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }
}
