import 'package:intl/intl.dart';

class Formatters {
  static String date(DateTime dt, {String pattern = 'MMM d, yyyy'}) =>
      DateFormat(pattern).format(dt);

  static String time(DateTime dt) => DateFormat.jm().format(dt);

  static String dateTime(DateTime dt) =>
      DateFormat('MMM d, yyyy • h:mm a').format(dt);

  static String relativeDate(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inDays == 0) return 'Today';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays} days ago';
    return date(dt);
  }

  static String currency(double amount, {String symbol = '\$'}) =>
      NumberFormat.currency(symbol: symbol, decimalDigits: 2).format(amount);

  static String compact(double amount) =>
      NumberFormat.compact().format(amount);

  static String truncate(String text, {int maxLength = 100}) {
    if (text.length <= maxLength) return text;
    return '${text.substring(0, maxLength)}...';
  }

  static String initials(String name) {
    final parts = name.trim().split(' ');
    if (parts.isEmpty) return '';
    if (parts.length == 1) return parts[0][0].toUpperCase();
    return '${parts[0][0]}${parts.last[0]}'.toUpperCase();
  }
}
