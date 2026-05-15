import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/client_profile.dart';
import '../../providers/user_provider.dart';
import '../../repositories/profile_repository.dart';

class PassportPage extends ConsumerStatefulWidget {
  const PassportPage({super.key});

  @override
  ConsumerState<PassportPage> createState() => _PassportPageState();
}

class _PassportPageState extends ConsumerState<PassportPage> {
  ClientProfile? _profile;
  bool _loading = true;
  String? _error;

  static const _gold = Color(0xFFC9A96E);
  static const _bg = Color(0xFF0A0A0F);

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final user = await ref.read(userProvider.future);
      final repo = ref.read(profileRepositoryProvider);
      final profile = await repo.getProfile(user.id);
      if (mounted) setState(() { _profile = profile; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = 'Could not load profile'; _loading = false; });
    }
  }

  double _conditionToFill(String condition) {
    switch (condition.toLowerCase()) {
      case 'healthy': return 1.0;
      case 'slightly damaged': return 0.75;
      case 'moderate damage': return 0.5;
      case 'severely damaged': return 0.25;
      default: return 0.5;
    }
  }

  String _formatScanDate(String? isoDate) {
    if (isoDate == null) return 'Not scanned yet';
    try {
      final dt = DateTime.parse(isoDate).toLocal();
      final diff = DateTime.now().difference(dt);
      if (diff.inHours < 1) return 'Just now';
      if (diff.inHours < 24) return '${diff.inHours}h ago';
      if (diff.inDays < 7) return '${diff.inDays}d ago';
      return '${dt.day}/${dt.month}/${dt.year}';
    } catch (_) {
      return 'Recently';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 18),
          onPressed: () => context.pop(),
        ),
        title: const Text(
          'BEAUTY PASSPORT',
          style: TextStyle(
            color: _gold,
            fontSize: 10,
            fontWeight: FontWeight.w700,
            letterSpacing: 2.0,
          ),
        ),
        centerTitle: true,
        actions: [
          if (_profile != null)
            IconButton(
              icon: const Icon(Icons.edit_outlined, color: _gold, size: 20),
              tooltip: 'Edit Profile',
              onPressed: () => context.push('/profile-review'),
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _gold))
          : _error != null
              ? _buildError()
              : _profile == null || !_profile!.profileComplete
                  ? _buildEmpty()
                  : _buildPassport(),
    );
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, color: Colors.white.withOpacity(0.4), size: 48),
          const SizedBox(height: 16),
          Text(_error!, style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 14)),
          const SizedBox(height: 24),
          _actionButton('Retry', Icons.refresh, _loadProfile),
        ],
      ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: _gold.withOpacity(0.3), width: 1),
              ),
              child: Icon(Icons.face_retouching_natural, color: _gold.withOpacity(0.5), size: 48),
            ),
            const SizedBox(height: 24),
            const Text(
              'No Beauty Passport Yet',
              style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Text(
              'Take a quick selfie and let AI build your personal beauty profile.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 14, height: 1.5),
            ),
            const SizedBox(height: 32),
            _actionButton('Start Face Scan', Icons.camera_alt_outlined, () => context.push('/face-scan')),
          ],
        ),
      ),
    );
  }

  Widget _buildPassport() {
    final p = _profile!;
    final confidencePct = (p.confidence * 100).toInt();
    final hairFill = _conditionToFill(p.hairCondition);

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 20),

          // Confidence ring
          Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: 200, height: 200,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: _gold.withOpacity(0.2), width: 1),
                ),
              ),
              Container(
                width: 160, height: 160,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: _gold.withOpacity(0.4), width: 1),
                ),
              ),
              Container(
                width: 120, height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: const LinearGradient(
                    colors: [Color(0xFFE8D3A2), _gold],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  boxShadow: [BoxShadow(color: _gold.withOpacity(0.4), blurRadius: 40)],
                ),
                child: Center(
                  child: Text(
                    '$confidencePct',
                    style: const TextStyle(color: _bg, fontSize: 42, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              Positioned(
                top: 0,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: _bg,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _gold),
                  ),
                  child: const Text(
                    'AI CONFIDENCE',
                    style: TextStyle(color: _gold, fontSize: 8, fontWeight: FontWeight.bold, letterSpacing: 1.0),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          const Text(
            'Digital Twin Identity',
            style: TextStyle(
              color: Colors.white, fontSize: 24,
              fontFamily: 'Playfair Display', fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Updated ${_formatScanDate(p.lastScanAt)} via Beautrix Scanner',
            style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12),
          ),
          const SizedBox(height: 32),

          // Stats grid
          Row(children: [
            Expanded(child: _buildStatCard('Hair Type', p.hairType.isNotEmpty ? p.hairType : '—')),
            const SizedBox(width: 16),
            Expanded(child: _buildStatCard('Skin Tone', p.skinTone.isNotEmpty ? p.skinTone : '—')),
          ]),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(child: _buildStatCard('Skin Type', p.skinCondition.isNotEmpty ? p.skinCondition : '—')),
            const SizedBox(width: 16),
            Expanded(child: _buildStatCard('Hair State', p.hairCondition.isNotEmpty ? p.hairCondition : '—')),
          ]),
          const SizedBox(height: 32),

          // Trait analysis
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.03),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.white.withOpacity(0.08)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'AI TRAIT ANALYSIS',
                  style: TextStyle(color: _gold, fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 1.5),
                ),
                const SizedBox(height: 16),
                _buildTraitBar('AI Confidence', p.confidence),
                const SizedBox(height: 12),
                _buildTraitBar('Hair Health', hairFill),
                const SizedBox(height: 12),
                _buildTraitBar('Profile Complete', p.profileComplete ? 1.0 : 0.5),
              ],
            ),
          ),

          // Hair concerns
          if (p.hairConcerns.isNotEmpty) ...[
            const SizedBox(height: 24),
            _buildSection('HAIR CONCERNS', Wrap(
              spacing: 8, runSpacing: 8,
              children: p.hairConcerns.map((c) => _buildChip(c)).toList(),
            )),
          ],

          // Allergies
          if (p.allergies.isNotEmpty) ...[
            const SizedBox(height: 24),
            _buildSection('ALLERGIES & SENSITIVITIES', Wrap(
              spacing: 8, runSpacing: 8,
              children: p.allergies.map((a) => _buildChip(a, color: Colors.red.shade900)).toList(),
            )),
          ],

          const SizedBox(height: 32),

          // Action buttons
          Row(children: [
            Expanded(
              child: _actionButton('Re-Scan', Icons.camera_alt_outlined, () => context.push('/face-scan')),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _actionButton('Edit Profile', Icons.edit_outlined, () => context.push('/profile-review')),
            ),
          ]),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.02),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              color: Colors.white.withOpacity(0.4), fontSize: 10,
              fontWeight: FontWeight.bold, letterSpacing: 1.0,
            ),
          ),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildTraitBar(String label, double fill) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500)),
            Text('${(fill * 100).toInt()}%', style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12)),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          height: 6,
          width: double.infinity,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(3),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: fill.clamp(0.0, 1.0),
            child: Container(
              decoration: BoxDecoration(color: _gold, borderRadius: BorderRadius.circular(3)),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSection(String title, Widget child) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.02),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: _gold, fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 1.5)),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }

  Widget _buildChip(String label, {Color? color}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: (color ?? _gold).withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: (color ?? _gold).withOpacity(0.3)),
      ),
      child: Text(label, style: TextStyle(color: color ?? _gold, fontSize: 12, fontWeight: FontWeight.w500)),
    );
  }

  Widget _actionButton(String label, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          border: Border.all(color: _gold.withOpacity(0.5)),
          borderRadius: BorderRadius.circular(16),
          color: _gold.withOpacity(0.05),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: _gold, size: 18),
            const SizedBox(width: 8),
            Text(label, style: const TextStyle(color: _gold, fontSize: 13, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}
