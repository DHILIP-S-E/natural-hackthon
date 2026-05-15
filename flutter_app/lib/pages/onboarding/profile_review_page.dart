import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../core/storage/local_storage.dart';
import '../../config/constants.dart';
import '../../providers/face_scan_provider.dart';
import '../../repositories/profile_repository.dart';

const _hairTypes = ['1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B', '3C', '4A', '4B', '4C'];
const _hairConditions = ['Healthy', 'Slightly damaged', 'Moderate damage', 'Severely damaged'];
const _hairConcernOptions = ['Frizz', 'Breakage', 'Dryness', 'Oiliness', 'Color-fade', 'Scalp irritation', 'Hair fall', 'Dandruff'];
const _skinTones = ['Fair', 'Light', 'Medium', 'Olive', 'Dark', 'Deep'];
const _skinConditions = ['Dry', 'Oily', 'Combination', 'Normal', 'Sensitive'];

class ProfileReviewPage extends ConsumerStatefulWidget {
  const ProfileReviewPage({super.key});

  @override
  ConsumerState<ProfileReviewPage> createState() => _ProfileReviewPageState();
}

class _ProfileReviewPageState extends ConsumerState<ProfileReviewPage> {
  final _allergyController = TextEditingController();
  bool _isSaving = false;
  String? _error;

  @override
  void dispose() {
    _allergyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(faceScanProvider);
    final profile = state.editedProfile;

    if (profile == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.scaffoldBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.bgGradient),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_rounded,
                          color: Color(0xFF1A1A2E)),
                      onPressed: () => context.go('/face-scan'),
                    ),
                    const Expanded(
                      child: Text(
                        'Review Your Profile',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 18,
                          color: Color(0xFF1A1A2E),
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.chipBg,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Text(
                        'Step 2 of 2',
                        style: TextStyle(
                          color: AppColors.primary,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              // AI confidence badge
              if (state.analysisResult != null)
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppColors.aiBubbleBorder),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.auto_awesome_rounded,
                            color: AppColors.primary, size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'AI analyzed your hair & skin with ${(state.analysisResult!.confidence * 100).toStringAsFixed(0)}% confidence. Edit any field below.',
                            style: const TextStyle(
                              fontSize: 12,
                              color: Color(0xFF666680),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(20, 4, 20, 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _SectionCard(
                        title: 'Hair Profile',
                        icon: Icons.face_retouching_natural,
                        children: [
                          _DropdownRow(
                            label: 'Hair Type',
                            value: profile.hairType,
                            options: _hairTypes,
                            onChanged: (v) => ref
                                .read(faceScanProvider.notifier)
                                .updateHairType(v),
                          ),
                          const SizedBox(height: 14),
                          _DropdownRow(
                            label: 'Hair Condition',
                            value: profile.hairCondition,
                            options: _hairConditions,
                            onChanged: (v) => ref
                                .read(faceScanProvider.notifier)
                                .updateHairCondition(v),
                          ),
                          const SizedBox(height: 14),
                          const Text(
                            'Hair Concerns',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF1A1A2E),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: _hairConcernOptions.map((concern) {
                              final selected =
                                  profile.hairConcerns.contains(concern);
                              return GestureDetector(
                                onTap: () => ref
                                    .read(faceScanProvider.notifier)
                                    .toggleHairConcern(concern),
                                child: AnimatedContainer(
                                  duration: const Duration(milliseconds: 150),
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 7),
                                  decoration: BoxDecoration(
                                    color: selected
                                        ? AppColors.primary
                                        : Colors.white,
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(
                                      color: selected
                                          ? AppColors.primary
                                          : AppColors.aiBubbleBorder,
                                    ),
                                  ),
                                  child: Text(
                                    concern,
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w500,
                                      color: selected
                                          ? Colors.white
                                          : const Color(0xFF666680),
                                    ),
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      _SectionCard(
                        title: 'Skin Profile',
                        icon: Icons.face_rounded,
                        children: [
                          _DropdownRow(
                            label: 'Skin Tone',
                            value: profile.skinTone,
                            options: _skinTones,
                            onChanged: (v) => ref
                                .read(faceScanProvider.notifier)
                                .updateSkinTone(v),
                          ),
                          const SizedBox(height: 14),
                          _DropdownRow(
                            label: 'Skin Condition',
                            value: profile.skinCondition,
                            options: _skinConditions,
                            onChanged: (v) => ref
                                .read(faceScanProvider.notifier)
                                .updateSkinCondition(v),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      _SectionCard(
                        title: 'Allergies',
                        icon: Icons.warning_amber_rounded,
                        children: [
                          if (profile.allergies.isNotEmpty) ...[
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: profile.allergies.map((a) {
                                return Chip(
                                  label: Text(a),
                                  deleteIcon: const Icon(Icons.close, size: 14),
                                  onDeleted: () {
                                    final updated =
                                        List<String>.from(profile.allergies)
                                          ..remove(a);
                                    ref
                                        .read(faceScanProvider.notifier)
                                        .updateAllergies(updated);
                                  },
                                  backgroundColor: const Color(0xFFFFF3CD),
                                  side: const BorderSide(
                                      color: Color(0xFFFFD966)),
                                  labelStyle: const TextStyle(fontSize: 12),
                                );
                              }).toList(),
                            ),
                            const SizedBox(height: 12),
                          ],
                          Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _allergyController,
                                  decoration: InputDecoration(
                                    hintText: 'e.g. PPD, Ammonia',
                                    hintStyle: const TextStyle(
                                        color: Color(0xFFB0A8C0), fontSize: 13),
                                    filled: true,
                                    fillColor: Colors.white,
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(10),
                                      borderSide: const BorderSide(
                                          color: Color(0xFFEEE6FF)),
                                    ),
                                    enabledBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(10),
                                      borderSide: const BorderSide(
                                          color: Color(0xFFEEE6FF)),
                                    ),
                                    contentPadding: const EdgeInsets.symmetric(
                                        horizontal: 12, vertical: 10),
                                  ),
                                  style: const TextStyle(fontSize: 13),
                                ),
                              ),
                              const SizedBox(width: 8),
                              IconButton(
                                onPressed: () {
                                  final text =
                                      _allergyController.text.trim();
                                  if (text.isEmpty) return;
                                  final updated = [
                                    ...profile.allergies,
                                    text
                                  ];
                                  ref
                                      .read(faceScanProvider.notifier)
                                      .updateAllergies(updated);
                                  _allergyController.clear();
                                },
                                icon: const Icon(Icons.add_circle_rounded,
                                    color: AppColors.primary),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      if (_error != null) ...[
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color:
                                Theme.of(context).colorScheme.errorContainer,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            _error!,
                            style: TextStyle(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onErrorContainer,
                              fontSize: 13,
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                      ],
                      // Save button
                      GestureDetector(
                        onTap: _isSaving ? null : () => _saveProfile(context),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          decoration: BoxDecoration(
                            gradient: _isSaving
                                ? null
                                : AppColors.primaryGradient,
                            color: _isSaving ? Colors.grey.shade300 : null,
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: _isSaving
                                ? null
                                : [
                                    BoxShadow(
                                      color:
                                          AppColors.primary.withOpacity(0.3),
                                      blurRadius: 12,
                                      offset: const Offset(0, 4),
                                    )
                                  ],
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              if (_isSaving)
                                const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                )
                              else
                                const Icon(Icons.check_rounded,
                                    color: Colors.white, size: 20),
                              const SizedBox(width: 10),
                              Text(
                                _isSaving ? 'Saving...' : 'Save & Continue',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 15,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _saveProfile(BuildContext context) async {
    setState(() {
      _isSaving = true;
      _error = null;
    });
    try {
      final state = ref.read(faceScanProvider);
      final profile = state.editedProfile!;
      final analysisId = state.analysisResult?.analysisId ?? '';

      final storage = ref.read(localStorageProvider);
      final customerId = await storage.getString(AppConstants.userKey) ?? '';

      final profileRepo = ref.read(profileRepositoryProvider);
      await profileRepo.saveProfile(
        customerId: customerId,
        analysisId: analysisId,
        profile: profile,
      );

      ref.read(faceScanProvider.notifier).reset();
      if (context.mounted) context.go('/tempo');
    } catch (e) {
      setState(() =>
          _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final List<Widget> children;

  const _SectionCard({
    required this.title,
    required this.icon,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.06),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: AppColors.primary, size: 18),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 15,
                  color: Color(0xFF1A1A2E),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }
}

class _DropdownRow extends StatelessWidget {
  final String label;
  final String value;
  final List<String> options;
  final ValueChanged<String> onChanged;

  const _DropdownRow({
    required this.label,
    required this.value,
    required this.options,
    required this.onChanged,
  });

  String get _safeValue =>
      options.contains(value) ? value : (options.isNotEmpty ? options.first : '');

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 120,
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: Color(0xFF1A1A2E),
            ),
          ),
        ),
        Expanded(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: AppColors.chipBg,
              borderRadius: BorderRadius.circular(10),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _safeValue,
                isExpanded: true,
                style: const TextStyle(
                  fontSize: 13,
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
                dropdownColor: Colors.white,
                items: options
                    .map((o) => DropdownMenuItem(value: o, child: Text(o)))
                    .toList(),
                onChanged: (v) {
                  if (v != null) onChanged(v);
                },
              ),
            ),
          ),
        ),
      ],
    );
  }
}
