import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../config/app_colors.dart';
import '../../core/api/api_client.dart';
import '../../core/api/endpoints.dart';
import '../../providers/beauty_providers.dart';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

class _ChatMessage {
  final String text;
  final bool isAi;
  final DateTime time;
  _ChatMessage({required this.text, required this.isAi}) : time = DateTime.now();
}

class _MessagesNotifier extends StateNotifier<List<_ChatMessage>> {
  _MessagesNotifier()
      : super([
          _ChatMessage(
            text: "Hi! I'm Beautrix Live AI. Show me your face, skin, or hair — or just ask me anything about your beauty.",
            isAi: true,
          ),
        ]);

  void add(_ChatMessage msg) => state = [...state, msg];
  void addAi(String text) => state = [...state, _ChatMessage(text: text, isAi: true)];
}

final _messagesProvider =
    StateNotifierProvider<_MessagesNotifier, List<_ChatMessage>>(
  (ref) => _MessagesNotifier(),
);

final _isListeningProvider = StateProvider<bool>((ref) => false);
final _isAnalyzingProvider = StateProvider<bool>((ref) => false);
final _sessionIdProvider = StateProvider<String?>((ref) => null);

const _concerns = [
  '✨ Skin glow',
  '💧 Hydration',
  '🧴 Skincare routine',
  '💇 Hairstyle',
  '🧔 Beard style',
  '💄 Makeup look',
  '🌙 Dark circles',
  '🔍 Pores & acne',
];

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

class BeautrixLivePage extends ConsumerStatefulWidget {
  const BeautrixLivePage({super.key});

  @override
  ConsumerState<BeautrixLivePage> createState() => _BeautrixLivePageState();
}

class _BeautrixLivePageState extends ConsumerState<BeautrixLivePage>
    with TickerProviderStateMixin {
  late final AnimationController _pulseCtrl;
  late final AnimationController _scanCtrl;
  final _scrollCtrl = ScrollController();
  final _inputCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _scanCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    _scanCtrl.dispose();
    _scrollCtrl.dispose();
    _inputCtrl.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // Build context string from beauty passport so AI has full profile context
  String _buildPassportContext(Map<String, dynamic>? passport) {
    if (passport == null) return '';
    final profile = passport['profile'] as Map<String, dynamic>? ?? {};
    final skin = passport['skin'] as Map<String, dynamic>? ?? {};
    final hair = passport['hair'] as Map<String, dynamic>? ?? {};
    final parts = <String>[];

    if (profile['dominant_archetype'] != null)
      parts.add('Archetype: ${profile['dominant_archetype']}');
    if (skin['type'] != null) parts.add('Skin type: ${skin['type']}');
    if (skin['tone'] != null) parts.add('Skin tone: ${skin['tone']}');
    if ((skin['concerns'] as List?)?.isNotEmpty == true)
      parts.add('Skin concerns: ${(skin['concerns'] as List).join(', ')}');
    if (hair['type'] != null) parts.add('Hair type: ${hair['type']}');
    if (hair['damage'] != null) parts.add('Hair damage level: ${hair['damage']}/5');
    if (profile['known_allergies'] != null &&
        (profile['known_allergies'] as List).isNotEmpty)
      parts.add('Allergies: ${(profile['known_allergies'] as List).join(', ')}');

    return parts.isEmpty ? '' : '[Customer Profile: ${parts.join(' | ')}]';
  }

  Future<void> _pickImageAndAnalyze() async {
    final picker = ImagePicker();
    final img = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (img == null) return;

    ref.read(_isAnalyzingProvider.notifier).state = true;
    ref.read(_messagesProvider.notifier).add(
          _ChatMessage(text: '📸 Photo captured. Analyzing...', isAi: false),
        );
    _scrollToBottom();

    try {
      final bytes = await File(img.path).readAsBytes();
      final base64Image = base64Encode(bytes);

      final api = ref.read(apiClientProvider);
      final res = await api.post<Map<String, dynamic>>(
        Endpoints.scanFace,
        data: {
          'photo_base64': base64Image,
          'photo_url': '',
        },
      );

      final analysis = res.data?['data']?['analysis'] as Map<String, dynamic>?;
      if (analysis != null) {
        final skinTone = analysis['skin']?['tone'] ?? 'your skin tone';
        final skinCond = analysis['skin']?['condition'] ?? 'combination';
        final skinIssues = (analysis['skin']?['issues'] as List?)?.join(', ') ?? '';
        final hairType = analysis['hair']?['type'] ?? '';
        final hairCond = analysis['hair']?['condition'] ?? '';

        final reply = StringBuffer('I can see your face clearly. ');
        reply.write('You have $skinTone skin with a $skinCond complexion. ');
        if (skinIssues.isNotEmpty) reply.write('I notice $skinIssues. ');
        if (hairType.isNotEmpty) reply.write('Your hair appears to be $hairType type ($hairCond). ');
        reply.write('Would you like personalized recommendations for your skin or hair?');

        ref.read(_messagesProvider.notifier).addAi(reply.toString());
      } else {
        ref.read(_messagesProvider.notifier).addAi(
              'I\'ve analyzed your photo. Ask me anything about what I see!',
            );
      }
    } catch (_) {
      ref.read(_messagesProvider.notifier).addAi(
            'I couldn\'t process the photo right now. Try asking me a question directly.',
          );
    } finally {
      if (mounted) ref.read(_isAnalyzingProvider.notifier).state = false;
      _scrollToBottom();
    }
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty) return;
    _inputCtrl.clear();

    ref.read(_messagesProvider.notifier).add(
          _ChatMessage(text: text.trim(), isAi: false),
        );
    ref.read(_isAnalyzingProvider.notifier).state = true;
    _scrollToBottom();

    try {
      final api = ref.read(apiClientProvider);
      final sessionId = ref.read(_sessionIdProvider);
      final passport = await ref.read(beautyPassportProvider.future).then(
            (p) => p,
            onError: (_) => null,
          );
      final passportContext = _buildPassportContext(passport);
      final history = ref
          .read(_messagesProvider)
          .map((m) => {'role': m.isAi ? 'assistant' : 'user', 'content': m.text})
          .toList();

      final messageWithContext = passportContext.isNotEmpty
          ? '$passportContext\n\nUser: $text'
          : text;

      final res = await api.post<Map<String, dynamic>>(
        Endpoints.chatbot,
        data: {
          'message': messageWithContext,
          'session_id': sessionId,
          'history': history.length > 10 ? history.sublist(history.length - 10) : history,
        },
      );

      final reply = res.data?['reply'] as String? ??
          'I\'m here to help with your beauty questions!';
      final newSessionId = res.data?['session_id'] as String?;

      if (newSessionId != null) {
        ref.read(_sessionIdProvider.notifier).state = newSessionId;
      }

      if (mounted) ref.read(_messagesProvider.notifier).addAi(reply);
    } catch (_) {
      if (mounted) {
        ref.read(_messagesProvider.notifier).addAi(
              'I\'m having trouble connecting right now. Please try again.',
            );
      }
    } finally {
      if (mounted) ref.read(_isAnalyzingProvider.notifier).state = false;
      _scrollToBottom();
    }
  }

  Future<void> _sendConcern(String concern) => _sendMessage(concern);

  void _toggleListening() {
    final current = ref.read(_isListeningProvider);
    ref.read(_isListeningProvider.notifier).state = !current;
    // Voice-to-text integration point — wire speech_to_text here when added
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(_messagesProvider);
    final isListening = ref.watch(_isListeningProvider);
    final isAnalyzing = ref.watch(_isAnalyzingProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0D0A1A),
      body: SafeArea(
        child: Column(
          children: [
            _Header(onClose: () => Navigator.of(context).pop()),
            _CameraViewfinder(
              pulseCtrl: _pulseCtrl,
              scanCtrl: _scanCtrl,
              isListening: isListening,
              onCapture: _pickImageAndAnalyze,
              onMicTap: _toggleListening,
            ),
            _ConcernChips(onTap: _sendConcern),
            Expanded(
              child: _ChatPanel(
                messages: messages,
                isAnalyzing: isAnalyzing,
                scrollCtrl: _scrollCtrl,
              ),
            ),
            _InputBar(
              controller: _inputCtrl,
              isListening: isListening,
              onMicTap: _toggleListening,
              onSend: () => _sendMessage(_inputCtrl.text),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

class _Header extends StatelessWidget {
  final VoidCallback onClose;
  const _Header({required this.onClose});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      child: Row(
        children: [
          GestureDetector(
            onTap: onClose,
            child: Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.arrow_back_ios_new_rounded,
                  color: Colors.white, size: 16),
            ),
          ),
          const SizedBox(width: 14),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ShaderMask(
                shaderCallback: (bounds) =>
                    AppColors.primaryGradient.createShader(bounds),
                child: const Text(
                  'BEAUTRIX LIVE AI',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                    letterSpacing: 1.5,
                  ),
                ),
              ),
              const Text(
                'Real-time beauty intelligence',
                style: TextStyle(fontSize: 11, color: Color(0xFF9B8FB5)),
              ),
            ],
          ),
          const Spacer(),
          _LiveBadge(),
        ],
      ),
    );
  }
}

class _LiveBadge extends StatefulWidget {
  @override
  State<_LiveBadge> createState() => _LiveBadgeState();
}

class _LiveBadgeState extends State<_LiveBadge>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
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
      builder: (_, __) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: Color.lerp(
            const Color(0xFFFF3D7F),
            const Color(0xFFFF6B9D),
            _ctrl.value,
          ),
          borderRadius: BorderRadius.circular(20),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.circle, color: Colors.white, size: 7),
            SizedBox(width: 5),
            Text(
              'LIVE',
              style: TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 1,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Camera Viewfinder
// ---------------------------------------------------------------------------

class _CameraViewfinder extends StatelessWidget {
  final AnimationController pulseCtrl;
  final AnimationController scanCtrl;
  final bool isListening;
  final VoidCallback onCapture;
  final VoidCallback onMicTap;

  const _CameraViewfinder({
    required this.pulseCtrl,
    required this.scanCtrl,
    required this.isListening,
    required this.onCapture,
    required this.onMicTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      height: 200,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          colors: [Color(0xFF1A1030), Color(0xFF0D0A1A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        border: Border.all(
          color: AppColors.primary.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(23),
        child: Stack(
          children: [
            if (isListening)
              Center(
                child: AnimatedBuilder(
                  animation: pulseCtrl,
                  builder: (_, __) {
                    return Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(5, (index) {
                        final delay = index * 0.2;
                        final val = math.sin((pulseCtrl.value * math.pi * 2) + delay);
                        final height = 20.0 + (val.abs() * 40.0);
                        return Container(
                          margin: const EdgeInsets.symmetric(horizontal: 4),
                          width: 4,
                          height: height,
                          decoration: BoxDecoration(
                            color: const Color(0xFFC9A96E),
                            borderRadius: BorderRadius.circular(2),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFFC9A96E).withOpacity(0.5),
                                blurRadius: 10,
                              ),
                            ],
                          ),
                        );
                      }),
                    );
                  },
                ),
              )
            else
              Center(
                child: AnimatedBuilder(
                  animation: pulseCtrl,
                  builder: (_, __) => Container(
                    width: 120,
                    height: 140,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(60),
                      border: Border.all(
                        color: const Color(0xFFC9A96E)
                            .withOpacity(0.3 + 0.4 * pulseCtrl.value),
                        width: 1.5,
                      ),
                    ),
                  ),
                ),
              ),
            AnimatedBuilder(
              animation: scanCtrl,
              builder: (_, __) {
                final y = scanCtrl.value * 140;
                return Positioned(
                  top: 30 + y,
                  left: 60,
                  right: 60,
                  child: Container(
                    height: 1.5,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.transparent,
                          const Color(0xFFC9A96E).withOpacity(0.7),
                          Colors.transparent,
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
            ..._corners(),
            const Positioned(
              top: 14,
              left: 16,
              child: Text(
                'AI VISION',
                style: TextStyle(
                  color: Color(0xFFC9A96E),
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.2,
                ),
              ),
            ),
            Positioned(
              bottom: 14,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _ViewfinderButton(
                    icon: Icons.camera_alt_outlined,
                    label: 'Capture',
                    onTap: onCapture,
                  ),
                  const SizedBox(width: 20),
                  _ViewfinderButton(
                    icon: isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                    label: isListening ? 'Listening…' : 'Speak',
                    onTap: onMicTap,
                    active: isListening,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _corners() {
    const size = 16.0;
    const thick = 2.0;
    const color = Color(0xFFC9A96E);
    return [
      _corner(top: 10, left: 10, size: size, thick: thick, color: color, topLeft: true),
      _corner(top: 10, right: 10, size: size, thick: thick, color: color, topRight: true),
      _corner(bottom: 10, left: 10, size: size, thick: thick, color: color, bottomLeft: true),
      _corner(bottom: 10, right: 10, size: size, thick: thick, color: color, bottomRight: true),
    ];
  }

  Widget _corner({
    double? top, double? bottom, double? left, double? right,
    required double size, required double thick, required Color color,
    bool topLeft = false, bool topRight = false,
    bool bottomLeft = false, bool bottomRight = false,
  }) {
    return Positioned(
      top: top, bottom: bottom, left: left, right: right,
      child: SizedBox(
        width: size,
        height: size,
        child: CustomPaint(
          painter: _CornerPainter(
            color: color, thickness: thick,
            topLeft: topLeft, topRight: topRight,
            bottomLeft: bottomLeft, bottomRight: bottomRight,
          ),
        ),
      ),
    );
  }
}

class _CornerPainter extends CustomPainter {
  final Color color;
  final double thickness;
  final bool topLeft, topRight, bottomLeft, bottomRight;

  _CornerPainter({
    required this.color, required this.thickness,
    this.topLeft = false, this.topRight = false,
    this.bottomLeft = false, this.bottomRight = false,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = thickness
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    if (topLeft) {
      canvas.drawLine(Offset(0, size.height), const Offset(0, 0), paint);
      canvas.drawLine(const Offset(0, 0), Offset(size.width, 0), paint);
    }
    if (topRight) {
      canvas.drawLine(Offset(size.width, size.height), Offset(size.width, 0), paint);
      canvas.drawLine(Offset(size.width, 0), Offset(0, 0), paint);
    }
    if (bottomLeft) {
      canvas.drawLine(const Offset(0, 0), Offset(0, size.height), paint);
      canvas.drawLine(Offset(0, size.height), Offset(size.width, size.height), paint);
    }
    if (bottomRight) {
      canvas.drawLine(Offset(size.width, 0), Offset(size.width, size.height), paint);
      canvas.drawLine(Offset(size.width, size.height), Offset(0, size.height), paint);
    }
  }

  @override
  bool shouldRepaint(_CornerPainter old) => false;
}

class _ViewfinderButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool active;

  const _ViewfinderButton({
    required this.icon, required this.label, required this.onTap, this.active = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: active
                  ? const LinearGradient(colors: [Color(0xFFFF3D7F), Color(0xFFFF6B9D)])
                  : AppColors.primaryGradient,
            ),
            child: Icon(icon, color: Colors.white, size: 18),
          ),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(color: Colors.white60, fontSize: 10)),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Concern chips
// ---------------------------------------------------------------------------

class _ConcernChips extends StatelessWidget {
  final void Function(String) onTap;
  const _ConcernChips({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        scrollDirection: Axis.horizontal,
        itemCount: _concerns.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          final concern = _concerns[i];
          return GestureDetector(
            onTap: () => onTap(concern),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.15),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.primary.withOpacity(0.3)),
              ),
              child: Text(
                concern,
                style: const TextStyle(
                  color: Color(0xFFD4B8FF),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Chat panel
// ---------------------------------------------------------------------------

class _ChatPanel extends StatelessWidget {
  final List<_ChatMessage> messages;
  final bool isAnalyzing;
  final ScrollController scrollCtrl;

  const _ChatPanel({
    required this.messages, required this.isAnalyzing, required this.scrollCtrl,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: scrollCtrl,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: messages.length + (isAnalyzing ? 1 : 0),
      itemBuilder: (_, i) {
        if (isAnalyzing && i == messages.length) return const _TypingIndicator();
        return _Bubble(msg: messages[i]);
      },
    );
  }
}

class _Bubble extends StatelessWidget {
  final _ChatMessage msg;
  const _Bubble({required this.msg});

  @override
  Widget build(BuildContext context) {
    final isAi = msg.isAi;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: isAi ? MainAxisAlignment.start : MainAxisAlignment.end,
        children: [
          if (isAi) ...[
            Container(
              width: 28,
              height: 28,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppColors.primaryGradient,
              ),
              child: const Center(
                child: Text('B',
                    style: TextStyle(
                        color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isAi
                    ? const Color(0xFF1E1533)
                    : AppColors.primary.withOpacity(0.85),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(isAi ? 4 : 16),
                  bottomRight: Radius.circular(isAi ? 16 : 4),
                ),
                border: isAi
                    ? Border.all(color: AppColors.primary.withOpacity(0.2))
                    : null,
              ),
              child: Text(
                msg.text,
                style: TextStyle(
                  color: isAi ? const Color(0xFFE8D8FF) : Colors.white,
                  fontSize: 13.5,
                  height: 1.5,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TypingIndicator extends StatefulWidget {
  const _TypingIndicator();

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: AppColors.primaryGradient,
            ),
            child: const Center(
              child: Text('B',
                  style: TextStyle(
                      color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF1E1533),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
              ),
              border: Border.all(color: AppColors.primary.withOpacity(0.2)),
            ),
            child: AnimatedBuilder(
              animation: _ctrl,
              builder: (_, __) => Row(
                mainAxisSize: MainAxisSize.min,
                children: List.generate(3, (i) {
                  final delay = i * 0.3;
                  final t = (_ctrl.value - delay).clamp(0.0, 1.0);
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppColors.primary.withOpacity(0.4 + 0.6 * t),
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Input bar
// ---------------------------------------------------------------------------

class _InputBar extends ConsumerWidget {
  final TextEditingController controller;
  final bool isListening;
  final VoidCallback onMicTap;
  final VoidCallback onSend;

  const _InputBar({
    required this.controller,
    required this.isListening,
    required this.onMicTap,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 10,
        bottom: MediaQuery.of(context).padding.bottom + 10,
      ),
      decoration: const BoxDecoration(
        color: Color(0xFF130E22),
        border: Border(top: BorderSide(color: Color(0xFF2A1F44), width: 1)),
      ),
      child: Row(
        children: [
          GestureDetector(
            onTap: onMicTap,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: isListening
                    ? const LinearGradient(
                        colors: [Color(0xFFFF3D7F), Color(0xFFFF6B9D)])
                    : AppColors.primaryGradient,
              ),
              child: Icon(
                isListening ? Icons.stop_rounded : Icons.mic_rounded,
                color: Colors.white,
                size: 20,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFF1E1533),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: const Color(0xFF2A1F44)),
              ),
              child: TextField(
                controller: controller,
                style: const TextStyle(color: Colors.white, fontSize: 14),
                decoration: const InputDecoration(
                  hintText: 'Ask about skin, hair, makeup…',
                  hintStyle: TextStyle(color: Color(0xFF6B5B8A), fontSize: 13),
                  border: InputBorder.none,
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                ),
                onSubmitted: (_) => onSend(),
              ),
            ),
          ),
          const SizedBox(width: 10),
          GestureDetector(
            onTap: onSend,
            child: Container(
              width: 44,
              height: 44,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppColors.primaryGradient,
              ),
              child: const Icon(Icons.send_rounded, color: Colors.white, size: 18),
            ),
          ),
        ],
      ),
    );
  }
}
