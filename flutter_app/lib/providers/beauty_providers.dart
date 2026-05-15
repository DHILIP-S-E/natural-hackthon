import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api/api_client.dart';
import '../core/api/endpoints.dart';
import '../repositories/user_repository.dart';

// ---------------------------------------------------------------------------
// Beauty Passport
// ---------------------------------------------------------------------------

final beautyPassportProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final api = ref.watch(apiClientProvider);
  final repo = ref.watch(userRepositoryProvider);
  final user = await repo.getMe();
  final res = await api.get<Map<String, dynamic>>(
    Endpoints.beautyPassport(user.id),
  );
  return res.data?['data'] as Map<String, dynamic>?;
});

// ---------------------------------------------------------------------------
// Next Best Recommendation
// ---------------------------------------------------------------------------

final nextRecommendationProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final api = ref.watch(apiClientProvider);
  final repo = ref.watch(userRepositoryProvider);
  final user = await repo.getMe();
  final res = await api.get<Map<String, dynamic>>(
    Endpoints.nextRecommendation(user.id),
  );
  return res.data?['data'] as Map<String, dynamic>?;
});

// ---------------------------------------------------------------------------
// Loyalty
// ---------------------------------------------------------------------------

final loyaltyProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final api = ref.watch(apiClientProvider);
  final res = await api.get<Map<String, dynamic>>(Endpoints.loyalty);
  return res.data?['data'] as Map<String, dynamic>?;
});

// ---------------------------------------------------------------------------
// Upcoming Appointment
// Returns the next confirmed/pending booking for the current customer.
// ---------------------------------------------------------------------------

final upcomingAppointmentProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final api = ref.watch(apiClientProvider);
  final today = DateTime.now();
  final dateStr =
      '${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}';
  final res = await api.get<Map<String, dynamic>>(
    Endpoints.bookings,
    queryParameters: {
      'status': 'confirmed',
      'date_from': dateStr,
      'per_page': 1,
    },
  );
  final bookings = res.data?['data']?['bookings'] as List<dynamic>?;
  if (bookings == null || bookings.isEmpty) return null;
  return bookings.first as Map<String, dynamic>;
});
