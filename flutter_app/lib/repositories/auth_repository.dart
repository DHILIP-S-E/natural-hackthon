import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api/api_client.dart';
import '../core/api/endpoints.dart';
import '../core/auth/auth_service.dart';
import '../core/storage/local_storage.dart';
import '../config/constants.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final client = ref.watch(apiClientProvider);
  final authService = ref.watch(authServiceProvider);
  final storage = ref.watch(localStorageProvider);
  return AuthRepository(client, authService, storage);
});

class AuthRepository {
  final ApiClient _client;
  final AuthService _authService;
  final LocalStorage _storage;

  AuthRepository(this._client, this._authService, this._storage);

  /// Send OTP to phone number.
  Future<void> sendOtp({required String phone}) async {
    await _client.post<Map<String, dynamic>>(
      Endpoints.sendOtp,
      data: {'phone': phone},
    );
  }

  /// Verify OTP — returns same map as loginPhone.
  Future<Map<String, dynamic>> verifyOtp({
    required String phone,
    required String otp,
  }) async {
    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.verifyOtp,
      data: {'phone': phone, 'otp': otp},
    );
    final data = response.data!;
    await _authService.saveTokens(
      token: data['jwt_token'] as String,
      refreshToken: data['refresh_token'] as String? ?? '',
    );
    await _storage.setString(AppConstants.userKey, data['customer_id'] as String);
    return data;
  }

  /// Email + password login.
  Future<Map<String, dynamic>> loginEmail({
    required String email,
    required String password,
  }) async {
    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.loginEmail,
      data: {'email': email, 'password': password},
    );
    final body = response.data!;
    final data = body['data'] as Map<String, dynamic>;
    await _authService.saveTokens(
      token: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String? ?? '',
    );
    final user = data['user'] as Map<String, dynamic>? ?? {};
    await _storage.setString(AppConstants.userKey, user['id'] as String? ?? '');
    return data;
  }

  /// Phone login (no OTP). Returns map with is_new_customer + face_scan_required.
  Future<Map<String, dynamic>> loginPhone({required String phone}) async {
    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.loginPhone,
      data: {'phone': phone, 'country': 'IN'},
    );
    final data = response.data!;
    await _authService.saveTokens(
      token: data['jwt_token'] as String,
      refreshToken: data['refresh_token'] as String? ?? '',
    );
    await _storage.setString(AppConstants.userKey, data['customer_id'] as String);
    return data;
  }

  /// Google login. Returns map with is_new_customer + face_scan_required.
  Future<Map<String, dynamic>> googleLogin({required String idToken}) async {
    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.loginGoogle,
      data: {'google_token': idToken},
    );
    final data = response.data!;
    await _authService.saveTokens(
      token: data['jwt_token'] as String,
      refreshToken: data['refresh_token'] as String? ?? '',
    );
    await _storage.setString(AppConstants.userKey, data['customer_id'] as String);
    return data;
  }

  Future<void> login({required String email, required String password}) =>
      loginEmail(email: email, password: password);

  Future<Map<String, dynamic>> register({
    required String firstName,
    required String lastName,
    required String email,
    required String password,
    String? phone,
  }) async {
    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.register,
      data: {
        'first_name': firstName,
        'last_name': lastName,
        'email': email,
        'password': password,
        if (phone != null && phone.isNotEmpty) 'phone': phone,
      },
    );
    final body = response.data!;
    final data = body['data'] as Map<String, dynamic>;
    await _authService.saveTokens(
      token: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String? ?? '',
    );
    final user = data['user'] as Map<String, dynamic>? ?? {};
    await _storage.setString(AppConstants.userKey, user['id'] as String? ?? '');
    return data;
  }

  Future<void> logout() async {
    try {
      await _client.post(Endpoints.logout);
    } finally {
      await _authService.logout();
      await _storage.clear();
    }
  }
}
