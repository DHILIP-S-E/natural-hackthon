import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api/api_client.dart';
import '../core/api/api_response.dart';
import '../core/api/endpoints.dart';
import '../models/user.dart';

final userRepositoryProvider = Provider<UserRepository>((ref) {
  final client = ref.watch(apiClientProvider);
  return UserRepository(client);
});

class UserRepository {
  final ApiClient _client;

  UserRepository(this._client);

  Future<User> getMe() async {
    final response = await _client.get<Map<String, dynamic>>(Endpoints.me);
    final wrapped = ApiResponse.fromJson(
      response.data!,
      (data) => User.fromJson(data as Map<String, dynamic>),
    );
    return wrapped.data!;
  }

  Future<User> getUserById(String id) async {
    final response = await _client.get<Map<String, dynamic>>(
      Endpoints.userById(id),
    );
    final wrapped = ApiResponse.fromJson(
      response.data!,
      (data) => User.fromJson(data as Map<String, dynamic>),
    );
    return wrapped.data!;
  }

  Future<User> updateProfile(Map<String, dynamic> data) async {
    final response = await _client.put<Map<String, dynamic>>(
      Endpoints.me,
      data: data,
    );
    final wrapped = ApiResponse.fromJson(
      response.data!,
      (data) => User.fromJson(data as Map<String, dynamic>),
    );
    return wrapped.data!;
  }
}
