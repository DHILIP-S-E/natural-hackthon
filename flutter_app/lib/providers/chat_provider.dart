import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/message.dart';

class ChatNotifier extends StateNotifier<List<Message>> {
  ChatNotifier() : super(_initialMessages);

  static final _initialMessages = <Message>[
    Message(
      id: '1',
      text:
          "Hello there,\nyou've not been lately drinking water properly and missing out your habit.\n\nLet's get back on track!",
      sender: MessageSender.ai,
      timestamp: DateTime.now().subtract(const Duration(minutes: 10)),
    ),
  ];

  void sendMessage(String text) {
    final userMessage = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      sender: MessageSender.user,
      timestamp: DateTime.now(),
    );
    state = [...state, userMessage];
    _simulateAiReply(text);
  }

  void _simulateAiReply(String userText) {
    Future.delayed(const Duration(milliseconds: 800), () {
      final aiMessage = Message(
        id: '${DateTime.now().millisecondsSinceEpoch}_ai',
        text: "Working on your notification setting!\nDone! Stay hydrated.",
        sender: MessageSender.ai,
        timestamp: DateTime.now(),
      );
      state = [...state, aiMessage];
    });
  }

  void clearChat() => state = [];
}

final chatProvider = StateNotifierProvider<ChatNotifier, List<Message>>((ref) {
  return ChatNotifier();
});

final chatIdeas = [
  '🙏 Pray',
  '🍿 Snacks',
  '🧘 Meditation',
  '🥛 Milk',
  '📚 Study',
];
