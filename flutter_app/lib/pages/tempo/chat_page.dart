import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_colors.dart';
import '../../providers/chat_provider.dart';
import '../../widgets/tempo/chat_bubble.dart';
import '../../widgets/tempo/chat_input_bar.dart';

class TempoChatPage extends ConsumerStatefulWidget {
  final String? initialText;

  const TempoChatPage({super.key, this.initialText});

  @override
  ConsumerState<TempoChatPage> createState() => _TempoChatPageState();
}

class _TempoChatPageState extends ConsumerState<TempoChatPage> {
  final ScrollController _scrollCtrl = ScrollController();

  @override
  void initState() {
    super.initState();
    if (widget.initialText != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(chatProvider.notifier).sendMessage(widget.initialText!);
      });
    }
  }

  @override
  void dispose() {
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatProvider);
    ref.listen(chatProvider, (_, __) => _scrollToBottom());

    return Scaffold(
      backgroundColor: AppColors.scaffoldBg,
      appBar: _ChatAppBar(),
      body: Column(
        children: [
          Expanded(
            child: Container(
              decoration: const BoxDecoration(gradient: AppColors.bgGradient),
              child: ListView.builder(
                controller: _scrollCtrl,
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                itemCount: messages.length,
                itemBuilder: (context, index) {
                  return ChatBubble(message: messages[index]);
                },
              ),
            ),
          ),
          ChatInputBar(
            onSend: (text) {
              ref.read(chatProvider.notifier).sendMessage(text);
            },
            onVoiceTap: () => context.push('/tempo/voice'),
          ),
        ],
      ),
    );
  }
}

class _ChatAppBar extends StatelessWidget implements PreferredSizeWidget {
  @override
  Size get preferredSize => const Size.fromHeight(56);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: Colors.white,
      elevation: 0,
      shadowColor: Colors.transparent,
      surfaceTintColor: Colors.white,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_rounded, size: 20, color: Color(0xFF1A1A2E)),
        onPressed: () => context.pop(),
      ),
      title: const Text(
        'TEMPO AI',
        style: TextStyle(
          fontWeight: FontWeight.w800,
          fontSize: 15,
          color: Color(0xFF1A1A2E),
          letterSpacing: 0.5,
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.edit_outlined, size: 20, color: Color(0xFF666680)),
          onPressed: () {},
        ),
        IconButton(
          icon: const Icon(Icons.content_copy_outlined, size: 20, color: Color(0xFF666680)),
          onPressed: () {},
        ),
        IconButton(
          icon: const Icon(Icons.more_vert_rounded, size: 20, color: Color(0xFF666680)),
          onPressed: () {},
        ),
      ],
    );
  }
}
