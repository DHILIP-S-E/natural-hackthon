import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../config/app_colors.dart';
import '../../core/storage/local_storage.dart';
import '../../config/constants.dart';
import '../../providers/face_scan_provider.dart';
import '../../repositories/profile_repository.dart';

class FaceScanPage extends ConsumerStatefulWidget {
  const FaceScanPage({super.key});

  @override
  ConsumerState<FaceScanPage> createState() => _FaceScanPageState();
}

class _FaceScanPageState extends ConsumerState<FaceScanPage> {
  final _picker = ImagePicker();

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(faceScanProvider);

    return Scaffold(
      backgroundColor: AppColors.scaffoldBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppColors.bgGradient),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 12),
                // Header
                Row(
                  children: [
                    if (Navigator.of(context).canPop())
                      IconButton(
                        icon: const Icon(Icons.arrow_back_ios_rounded,
                            color: Color(0xFF1A1A2E)),
                        onPressed: () => context.pop(),
                      ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.chipBg,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Text(
                        'Step 1 of 2',
                        style: TextStyle(
                          color: AppColors.primary,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Text(
                  'Your Beauty Profile',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                        color: const Color(0xFF1A1A2E),
                      ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Take a selfie and our AI will analyze your hair & skin to personalize your salon experience.',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF666680),
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 32),
                // Photo preview / capture area
                Expanded(
                  child: state.hasImage
                      ? _PhotoPreview(imageFile: state.imageFile!)
                      : const _CaptureGuide(),
                ),
                const SizedBox(height: 24),
                if (state.error != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.errorContainer,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      state.error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onErrorContainer,
                        fontSize: 13,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],
                // Action buttons
                if (!state.hasImage) ...[
                  _ActionButton(
                    icon: Icons.camera_alt_rounded,
                    label: 'Take Selfie',
                    gradient: AppColors.primaryGradient,
                    onTap: () => _captureImage(ImageSource.camera),
                  ),
                  const SizedBox(height: 12),
                  _ActionButton(
                    icon: Icons.photo_library_rounded,
                    label: 'Choose from Gallery',
                    gradient: const LinearGradient(
                      colors: [Color(0xFF6B7280), Color(0xFF9CA3AF)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    onTap: () => _captureImage(ImageSource.gallery),
                  ),
                ] else ...[
                  if (state.isBusy)
                    _LoadingAnalysis(
                      message: state.isUploading
                          ? 'Uploading photo...'
                          : 'AI analyzing your hair & skin...',
                    )
                  else ...[
                    _ActionButton(
                      icon: Icons.auto_awesome_rounded,
                      label: 'Analyze with AI',
                      gradient: AppColors.primaryGradient,
                      onTap: () => _analyzePhoto(context),
                    ),
                    const SizedBox(height: 12),
                    TextButton.icon(
                      onPressed: () =>
                          ref.read(faceScanProvider.notifier).reset(),
                      icon: const Icon(Icons.refresh_rounded, size: 18),
                      label: const Text('Retake Photo'),
                      style: TextButton.styleFrom(
                        foregroundColor: AppColors.primary,
                      ),
                    ),
                  ],
                ],
                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _captureImage(ImageSource source) async {
    try {
      final xFile = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      if (xFile == null) return;
      ref.read(faceScanProvider.notifier).setImage(File(xFile.path));
    } catch (e) {
      ref
          .read(faceScanProvider.notifier)
          .setError('Could not access camera: $e');
    }
  }

  Future<void> _analyzePhoto(BuildContext context) async {
    final notifier = ref.read(faceScanProvider.notifier);
    final imageFile = ref.read(faceScanProvider).imageFile;
    if (imageFile == null) return;

    notifier.setError(null);
    notifier.setUploading(true);

    try {
      final storage = ref.read(localStorageProvider);
      final customerId =
          await storage.getString(AppConstants.userKey) ?? 'guest_${DateTime.now().millisecondsSinceEpoch}';

      notifier.setUploading(false);
      notifier.setAnalyzing(true);

      final profileRepo = ref.read(profileRepositoryProvider);
      final result = await profileRepo.scanFace(
        customerId: customerId,
        imageFile: imageFile,
      );

      notifier.setAnalysisResult(result);
      notifier.setAnalyzing(false);

      if (context.mounted) {
        context.go('/profile-review');
      }
    } catch (e) {
      notifier.setUploading(false);
      notifier.setAnalyzing(false);
      notifier.setError(
          'Analysis failed: ${e.toString().replaceFirst('Exception: ', '')}');
    }
  }
}

class _CaptureGuide extends StatelessWidget {
  const _CaptureGuide();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.aiBubbleBorder, width: 2),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.06),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppColors.primaryGradient.scale(0.15),
              border: Border.all(color: AppColors.primaryLight, width: 2),
            ),
            child: const Icon(
              Icons.face_rounded,
              size: 52,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Position your face in good lighting',
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 16,
              color: Color(0xFF1A1A2E),
            ),
          ),
          const SizedBox(height: 16),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 32),
            child: Column(
              children: [
                _Tip(icon: Icons.wb_sunny_outlined, text: 'Use natural or bright lighting'),
                SizedBox(height: 8),
                _Tip(icon: Icons.face_retouching_natural, text: 'Show hair clearly in frame'),
                SizedBox(height: 8),
                _Tip(icon: Icons.no_photography_outlined, text: 'Remove hat or accessories'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Tip extends StatelessWidget {
  final IconData icon;
  final String text;
  const _Tip({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.primary),
        const SizedBox(width: 8),
        Text(
          text,
          style: const TextStyle(fontSize: 13, color: Color(0xFF666680)),
        ),
      ],
    );
  }
}

class _PhotoPreview extends StatelessWidget {
  final File imageFile;
  const _PhotoPreview({required this.imageFile});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.12),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Image.file(
        imageFile,
        fit: BoxFit.cover,
        width: double.infinity,
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final LinearGradient gradient;
  final VoidCallback? onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.gradient,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          gradient: onTap != null ? gradient : null,
          color: onTap == null ? Colors.grey.shade300 : null,
          borderRadius: BorderRadius.circular(16),
          boxShadow: onTap != null
              ? [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  )
                ]
              : null,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(width: 10),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w700,
                fontSize: 15,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LoadingAnalysis extends StatelessWidget {
  final String message;
  const _LoadingAnalysis({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.chipBg,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          const SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: AppColors.primary,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

extension on LinearGradient {
  LinearGradient scale(double factor) => LinearGradient(
        colors: colors
            .map((c) => Color.fromARGB(
                  (c.alpha * factor).round().clamp(0, 255),
                  c.red,
                  c.green,
                  c.blue,
                ))
            .toList(),
        begin: begin,
        end: end,
      );
}
