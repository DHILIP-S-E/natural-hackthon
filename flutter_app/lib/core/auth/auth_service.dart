import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../config/constants.dart';
import '../storage/local_storage.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  final storage = ref.watch(localStorageProvider);
  return AuthService(storage);
});

class AuthService {
  final LocalStorage _storage;
  final GoogleSignIn _googleSignIn = GoogleSignIn(scopes: ['email', 'profile']);

  AuthService(this._storage);

  Future<bool> isAuthenticated() async {
    final token = await _storage.getSecure(AppConstants.tokenKey);
    return token != null && token.isNotEmpty;
  }

  Future<void> saveTokens({
    required String token,
    required String refreshToken,
  }) async {
    await Future.wait([
      _storage.saveSecure(AppConstants.tokenKey, token),
      _storage.saveSecure(AppConstants.refreshTokenKey, refreshToken),
    ]);
  }

  Future<void> logout() async {
    await Future.wait([
      _storage.clearSecure(),
      _storage.clear(),
      _googleSignIn.signOut(),
    ]);
  }

  Future<GoogleSignInAccount?> signInWithGoogle() async {
    return _googleSignIn.signIn();
  }

  Future<String?> getGoogleIdToken() async {
    final account = await _googleSignIn.signInSilently();
    if (account == null) return null;
    final auth = await account.authentication;
    return auth.idToken;
  }
}
