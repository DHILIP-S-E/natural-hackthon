import 'package:equatable/equatable.dart';

enum MessageSender { ai, user }

class Message extends Equatable {
  final String id;
  final String text;
  final MessageSender sender;
  final DateTime timestamp;

  const Message({
    required this.id,
    required this.text,
    required this.sender,
    required this.timestamp,
  });

  bool get isUser => sender == MessageSender.user;

  @override
  List<Object?> get props => [id, text, sender, timestamp];
}
