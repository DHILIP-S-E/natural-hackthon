import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../config/app_colors.dart';

// ---------------------------------------------------------------------------
// Providers
// ---------------------------------------------------------------------------

final _messagesProvider =
    StateNotifierProvider<_MessagesNotifier, List<_ChatMessage>>(
  (ref) => _MessagesNotifier(),
);

final _isListeningProvider = StateProvider<bool>((ref) => false);
final _isAnalyzingProvider = StateProvider<bool>((ref) => false);
final _capturedImageProvider = StateProvider<String?>((ref) => null);

class _ChatMessage {
  final String text;
  final bool isAi;
  final DateTime time;
  _ChatMessage({required this.text, required this.isAi})
      : time = DateTime.now();
}

class _MessagesNotifier extends StateNotifier<List<_ChatMessage>> {
  _MessagesNotifier()
      : super([
          _ChatMessage(
            text:
                "Hi! I'm Beautrix Live AI. Show me your face, skin, or hair — or just ask me anything about your beauty routine.",
            isAi: true,
          ),
        ]);

  void addMessage(_ChatMessage msg) => state = [...state, msg];

  void addAiReply(String text) {
    state = [...state, _ChatMessage(text: text, isAi: true)];
  }
}

// ---------------------------------------------------------------------------
// Concern chips data
// ---------------------------------------------------------------------------

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

const _aiReplies = {
  '✨ Skin glow': [
    "Your skin has a natural warmth to it — a Vitamin C serum in the morning will amplify that glow beautifully.",
    "For instant radiance, try a gentle glycolic acid toner twice a week. Pair it with SPF 50 in the morning.",
  ],
  '💧 Hydration': [
    "Hydration starts from within. Add a hyaluronic acid serum under your moisturizer — it holds 1000x its weight in water.",
    "Your skin may be dehydrated rather than dry. Layer a light water-gel moisturizer morning and night.",
  ],
  '🧴 Skincare routine': [
    "For your skin tone, I'd suggest: AM — cleanser → Vitamin C → SPF. PM — cleanser → retinol → peptide moisturizer.",
    "Start simple: a gentle cleanser, niacinamide serum, and a non-comedogenic moisturizer. Consistency is everything.",
  ],
  '💇 Hairstyle': [
    "Based on what I can see, a textured crop or layered cut would frame your face shape beautifully.",
    "Consider a mid-fade with soft texture on top — it's modern, low maintenance, and universally flattering.",
  ],
  '🧔 Beard style': [
    "A sculpted short boxed beard would sharpen your jawline and add definition to your face.",
    "Try a stubble fade — clean neck line, full cheeks. Clean, sharp, and effortlessly stylish.",
  ],
  '💄 Makeup look': [
    "A dewy glass skin base with a subtle nude lip and defined brows would be stunning for your tone.",
    "Try a warm terracotta eye with a glossy nude lip — it complements warm skin tones perfectly.",
  ],
  '🌙 Dark circles': [
    "Use a caffeine-infused eye cream morning and night. Cold spoon compresses for 5 minutes also work wonders.",
    "Dark circles here look pigmentation-related. A vitamin K eye cream and good sleep hygiene will help significantly.",
  ],
  '🔍 Pores & acne': [
    "A BHA (salicylic acid) cleanser twice a week will clear pores without stripping your skin.",
    "For visible pores, niacinamide 10% is your best friend. It visibly tightens and mattifies over 4–6 weeks.",
  ],
};

String _getReply(String concern) {
  final replies = _aiReplies[concern] ?? ["Let me analyze that for you — great question!"];
  return replies[math.Random().nextInt(replies.length)];
}

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

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final img = await picker.pickImage(source: ImageSource.camera);
    if (img == null) return;

    ref.read(_capturedImageProvider.notifier).state = img.path;
    ref.read(_isAnalyzingProvider.notifier).state = true;

    ref.read(_messagesProvider.notifier).addMessage(
          _ChatMessage(text: "📸 Photo captured. Analyzing...", isAi: false),
        );

    await Future.delayed(const Duration(seconds: 2));

    ref.read(_isAnalyzingProvider.notifier).state = false;
    ref.read(_messagesProvider.notifier).addAiReply(
      "I can see your skin clearly now. You have a warm undertone with slightly oily T-zone. "
      "I'd recommend a niacinamide serum to balance sebum, and a lightweight gel moisturizer. "
      "Your overall complexion looks healthy — keep up your current routine!",
    );
    _scrollToBottom();
  }

  Future<void> _toggleListening() async {
    final isListening = ref.read(_isListeningProvider);
    ref.read(_isListeningProvider.notifier).state = !isListening;

    if (!isListening) {
      await Future.delayed(const Duration(seconds: 3));
      if (!mounted) return;
      ref.read(_isListeningProvider.notifier).state = false;
      ref.read(_messagesProvider.notifier).addMessage(
            _ChatMessage(text: "How is my skin looking today?", isAi: false),
          );
      await Future.delayed(const Duration(milliseconds: 800));
      if (!mounted) return;
      ref.read(_messagesProvider.notifier).addAiReply(
        "Your skin looks vibrant today! I notice a slight oiliness around the nose — "
        "blotting papers or a mattifying primer would keep you fresh all day.",
      );
      _scrollToBottom();
    }
  }

  Future<void> _sendConcern(String concern) async {
    ref.read(_messagesProvider.notifier).addMessage(
          _ChatMessage(text: concern, isAi: false),
        );
    ref.read(_isAnalyzingProvider.notifier).state = true;
    _scrollToBottom();

    await Future.delayed(const Duration(milliseconds: 900));
    if (!mounted) return;

    ref.read(_isAnalyzingProvider.notifier).state = false;
    ref.read(_messagesProvider.notifier).addAiReply(_getReply(concern));
    _scrollToBottom();
  }

  Future<void> _sendText() async {
    final text = _inputCtrl.text.trim();
    if (text.isEmpty) return;
    _inputCtrl.clear();

    ref.read(_messagesProvider.notifier).addMessage(
          _ChatMessage(text: text, isAi: false),
        );
    ref.read(_isAnalyzingProvider.notifier).state = true;
    _scrollToBottom();

    await Future.delayed(const Duration(milliseconds: 900));
    if (!mounted) return;

    ref.read(_isAnalyzingProvider.notifier).state = false;
    ref.read(_messagesProvider.notifier).addAiReply(
      "Great question! Based on what I can see and your beauty profile, "
      "I'd recommend focusing on a consistent AM/PM routine. "
      "Hydration, SPF, and a targeted serum for your concern will deliver visible results in 4–6 weeks.",
    );
    _scrollToBottom();
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
              onCapture: _pickImage,
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
              onSend: _sendText,
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

  const _CameraViewfinder({
    required this.pulseCtrl,
    required this.scanCtrl,
    required this.isListening,
    required this.onCapture,
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
            // Face frame
            Center(
              child: AnimatedBuilder(
                animation: pulseCtrl,
                builder: (_, __) => Container(
                  width: 120,
                  height: 140,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(60),
                    border: Border.all(
                      color: AppColors.primary
                          .withOpacity(0.3 + 0.4 * pulseCtrl.value),
                      width: 1.5,
                    ),
                  ),
                ),
              ),
            ),
            // Scan line
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
                          AppColors.primary.withOpacity(0.7),
                          Colors.transparent,
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
            // Corner brackets
            ..._corners(),
            // Labels
            const Positioned(
              top: 14,
              left: 16,
              child: Text(
                'AI VISION',
                style: TextStyle(
                  color: Color(0xFF7C3AED),
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
                    icon: isListening
                        ? Icons.mic_rounded
                        : Icons.mic_none_rounded,
                    label: isListening ? 'Listening…' : 'Speak',
                    onTap: () {},
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
    const color = Color(0xFF7C3AED);
    return [
      _corner(top: 10, left: 10, size: size, thick: thick, color: color,
          topLeft: true),
      _corner(top: 10, right: 10, size: size, thick: thick, color: color,
          topRight: true),
      _corner(bottom: 10, left: 10, size: size, thick: thick, color: color,
          bottomLeft: true),
      _corner(bottom: 10, right: 10, size: size, thick: thick, color: color,
          bottomRight: true),
    ];
  }

  Widget _corner({
    double? top,
    double? bottom,
    double? left,
    double? right,
    required double size,
    required double thick,
    required Color color,
    bool topLeft = false,
    bool topRight = false,
    bool bottomLeft = false,
    bool bottomRight = false,
  }) {
    return Positioned(
      top: top,
      bottom: bottom,
      left: left,
      right: right,
      child: SizedBox(
        width: size,
        height: size,
        child: CustomPaint(
          painter: _CornerPainter(
            color: color,
            thickness: thick,
            topLeft: topLeft,
            topRight: topRight,
            bottomLeft: bottomLeft,
            bottomRight: bottomRight,
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
    required this.color,
    required this.thickness,
    this.topLeft = false,
    this.topRight = false,
    this.bottomLeft = false,
    this.bottomRight = false,
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
      canvas.drawLine(Offset(size.width, size.height),
          Offset(size.width, 0), paint);
      canvas.drawLine(
          Offset(size.width, 0), Offset(0, 0), paint);
    }
    if (bottomLeft) {
      canvas.drawLine(const Offset(0, 0), Offset(0, size.height), paint);
      canvas.drawLine(
          Offset(0, size.height), Offset(size.width, size.height), paint);
    }
    if (bottomRight) {
      canvas.drawLine(
          Offset(size.width, 0), Offset(size.width, size.height), paint);
      canvas.drawLine(Offset(size.width, size.height), Offset(0, size.height),
          paint);
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
    required this.icon,
    required this.label,
    required this.onTap,
    this.active = false,
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
                  ? const LinearGradient(
                      colors: [Color(0xFFFF3D7F), Color(0xFFFF6B9D)],
                    )
                  : AppColors.primaryGradient,
            ),
            child: Icon(icon, color: Colors.white, size: 18),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(color: Colors.white60, fontSize: 10),
          ),
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
                border: Border.all(
                  color: AppColors.primary.withOpacity(0.3),
                ),
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
    required this.messages,
    required this.isAnalyzing,
    required this.scrollCtrl,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: scrollCtrl,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: messages.length + (isAnalyzing ? 1 : 0),
      itemBuilder: (_, i) {
        if (isAnalyzing && i == messages.length) {
          return const _TypingIndicator();
        }
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
        mainAxisAlignment:
            isAi ? MainAxisAlignment.start : MainAxisAlignment.end,
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
                child: Text('B', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
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
                      color: Colors.white,
                      fontSize: 13,
                      fontWeight: FontWeight.bold)),
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
              child: const Icon(Icons.send_rounded,
                  color: Colors.white, size: 18),
            ),
          ),
        ],
      ),
    );
  }
}
