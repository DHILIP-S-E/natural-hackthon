import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../repositories/user_repository.dart';

final userProvider = FutureProvider<User>((ref) async {
  final repo = ref.watch(userRepositoryProvider);
  return repo.getMe();
});

// Auth form state
class AuthFormState {
  final String email;
  final String password;
  final bool isLoading;
  final String? error;

  const AuthFormState({
    this.email = '',
    this.password = '',
    this.isLoading = false,
    this.error,
  });

  AuthFormState copyWith({
    String? email,
    String? password,
    bool? isLoading,
    String? error,
  }) {
    return AuthFormState(
      email: email ?? this.email,
      password: password ?? this.password,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class AuthFormNotifier extends StateNotifier<AuthFormState> {
  AuthFormNotifier() : super(const AuthFormState());

  void setEmail(String email) => state = state.copyWith(email: email);
  void setPassword(String password) => state = state.copyWith(password: password);

  void setLoading(bool loading) => state = state.copyWith(isLoading: loading);

  void setError(String? error) => state = state.copyWith(error: error);

  void reset() => state = const AuthFormState();
}

final authFormProvider =
    StateNotifierProvider<AuthFormNotifier, AuthFormState>((ref) {
  return AuthFormNotifier();
});
