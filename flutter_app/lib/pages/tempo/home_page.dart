import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;
import '../../config/app_colors.dart';
import '../../providers/user_provider.dart';
import '../../providers/beauty_providers.dart';
import '../beautrix/beautrix_live_page.dart';

class TempoHomePage extends ConsumerStatefulWidget {
  const TempoHomePage({super.key});

  @override
  ConsumerState<TempoHomePage> createState() => _TempoHomePageState();
}

class _TempoHomePageState extends ConsumerState<TempoHomePage>
    with SingleTickerProviderStateMixin {
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
      backgroundColor: const Color(0xFF0A0A0F),
      body: Stack(
        children: [
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
                const SliverToBoxAdapter(child: SizedBox(height: 30)),
                SliverToBoxAdapter(child: _HeroOrbSection(orbCtrl: _orbCtrl)),
                const SliverToBoxAdapter(child: SizedBox(height: 40)),
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: _SmartAppointmentCard(),
                  ),
                ),
                const SliverToBoxAdapter(child: SizedBox(height: 24)),
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: _BeautyPassCard(),
                  ),
                ),
                const SliverToBoxAdapter(child: SizedBox(height: 24)),
                const SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 24),
                    child: _RecommendationCard(),
                  ),
                ),
                const SliverToBoxAdapter(child: SizedBox(height: 120)),
              ],
            ),
          ),
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

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

class _PremiumHeader extends ConsumerWidget {
  const _PremiumHeader();

  String _greeting() {
    final h = DateTime.now().hour;
    if (h < 12) return 'GOOD MORNING';
    if (h < 17) return 'GOOD AFTERNOON';
    return 'GOOD EVENING';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userProvider);
    final name = userAsync.when(
      data: (u) => u.firstName,
      loading: () => '...',
      error: (_, __) => 'Guest',
    );

    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _greeting(),
                style: const TextStyle(
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
          GestureDetector(
            onTap: () => context.push('/tempo/passport'),
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.05),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white.withOpacity(0.1)),
              ),
              child: const Icon(Icons.person_outline, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// AI Orb Hero
// ---------------------------------------------------------------------------

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
                        ),
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

// ---------------------------------------------------------------------------
// Smart Appointment Card — real data
// ---------------------------------------------------------------------------

class _SmartAppointmentCard extends ConsumerWidget {
  const _SmartAppointmentCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final apptAsync = ref.watch(upcomingAppointmentProvider);

    return apptAsync.when(
      loading: () => _ApptSkeleton(),
      error: (_, __) => const SizedBox.shrink(),
      data: (appt) {
        if (appt == null) return const SizedBox.shrink();

        final service = appt['service_name'] as String? ?? 'Appointment';
        final dateRaw = appt['scheduled_at'] as String?;
        final dateLabel = dateRaw != null
            ? _formatApptDate(DateTime.parse(dateRaw))
            : 'Upcoming';
        final salon = appt['location_name'] as String? ?? 'Naturals Salon';
        final aiInsight = appt['pre_visit_tip'] as String?;

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
                  GestureDetector(
                    onTap: () => context.push('/tempo/bookings'),
                    child: Icon(Icons.arrow_forward_ios,
                        color: Colors.white.withOpacity(0.3), size: 12),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                '$salon • $dateLabel',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontFamily: 'Playfair Display',
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                service,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.6),
                  fontSize: 14,
                ),
              ),
              if (aiInsight != null) ...[
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFC9A96E).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                        color: const Color(0xFFC9A96E).withOpacity(0.2)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.auto_awesome,
                          color: Color(0xFFC9A96E), size: 16),
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
                              aiInsight,
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
            ],
          ),
        );
      },
    );
  }

  String _formatApptDate(DateTime dt) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final tomorrow = today.add(const Duration(days: 1));
    final apptDay = DateTime(dt.year, dt.month, dt.day);

    final timeStr =
        '${dt.hour > 12 ? dt.hour - 12 : dt.hour}:${dt.minute.toString().padLeft(2, '0')} ${dt.hour >= 12 ? 'PM' : 'AM'}';

    if (apptDay == today) return 'Today $timeStr';
    if (apptDay == tomorrow) return 'Tomorrow $timeStr';

    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[dt.month]} ${dt.day} $timeStr';
  }
}

class _ApptSkeleton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.03),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _ShimmerBox(width: 160, height: 10),
          const SizedBox(height: 16),
          _ShimmerBox(width: 220, height: 18),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Beauty Pass Card — real loyalty data
// ---------------------------------------------------------------------------

class _BeautyPassCard extends ConsumerWidget {
  const _BeautyPassCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final loyaltyAsync = ref.watch(loyaltyProvider);

    return loyaltyAsync.when(
      loading: () => _ShimmerBox(width: double.infinity, height: 100),
      error: (_, __) => const SizedBox.shrink(),
      data: (loyalty) {
        final tier = loyalty?['tier'] as String? ?? 'Member';
        final points = (loyalty?['total_points'] as num?)?.toInt() ?? 0;
        final rewards = (loyalty?['redeemable_rewards'] as List?)?.length ?? 0;
        final tierLabel = tier[0].toUpperCase() + tier.substring(1);

        return GestureDetector(
          onTap: () => context.push('/tempo/pass'),
          child: Container(
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
                    Text(
                      'BEAUTRIX $tierLabel'.toUpperCase(),
                      style: const TextStyle(
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
                      '${points.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (m) => '${m[1]},')} pts · $rewards rewards',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.6),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
                Container(
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
              ],
            ),
          ),
        );
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Recommendation Card — real AI data
// ---------------------------------------------------------------------------

class _RecommendationCard extends ConsumerWidget {
  const _RecommendationCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final recAsync = ref.watch(nextRecommendationProvider);

    return recAsync.when(
      loading: () => _ShimmerBox(width: double.infinity, height: 160),
      error: (_, __) => const SizedBox.shrink(),
      data: (rec) {
        if (rec == null) return const SizedBox.shrink();

        final service = rec['recommended_service'] as String? ?? 'Personalized Service';
        final reasoning = rec['reasoning'] as String? ?? '';
        final urgency = (rec['urgency_score'] as num?)?.toInt() ?? 0;

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
                  const Spacer(),
                  if (urgency > 0)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: urgency >= 7
                            ? const Color(0xFFFF3D7F).withOpacity(0.15)
                            : const Color(0xFFC9A96E).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        'Urgency $urgency/10',
                        style: TextStyle(
                          color: urgency >= 7
                              ? const Color(0xFFFF3D7F)
                              : const Color(0xFFC9A96E),
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                service,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontFamily: 'Playfair Display',
                  fontWeight: FontWeight.w600,
                ),
              ),
              if (reasoning.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  reasoning,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.6),
                    fontSize: 13,
                    height: 1.5,
                  ),
                ),
              ],
              const SizedBox(height: 20),
              GestureDetector(
                onTap: () => context.push('/tempo/bookings'),
                child: Container(
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
              ),
            ],
          ),
        );
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Bottom Nav
// ---------------------------------------------------------------------------

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
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _NavItem(icon: Icons.home_outlined, label: 'Home', active: true, route: '/tempo'),
              _NavItem(icon: Icons.explore_outlined, label: 'Explore', active: false, route: '/tempo/passport'),
              _NavItem(icon: Icons.calendar_today_outlined, label: 'Book', active: false, route: '/tempo/bookings'),
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

  const _NavItem({
    required this.icon,
    required this.label,
    required this.active,
    required this.route,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        if (!active) context.push(route);
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

// ---------------------------------------------------------------------------
// Shared shimmer widget
// ---------------------------------------------------------------------------

class _ShimmerBox extends StatefulWidget {
  final double width;
  final double height;

  const _ShimmerBox({required this.width, required this.height});

  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            gradient: LinearGradient(
              begin: Alignment(-1.0 + 2 * _ctrl.value, 0),
              end: Alignment(1.0 + 2 * _ctrl.value, 0),
              colors: [
                Colors.white.withOpacity(0.03),
                Colors.white.withOpacity(0.07),
                Colors.white.withOpacity(0.03),
              ],
            ),
          ),
        );
      },
    );
  }
}
