import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

final localStorageProvider = Provider<LocalStorage>((ref) {
  return LocalStorage();
});

class LocalStorage {
  final FlutterSecureStorage _secure = const FlutterSecureStorage();
  SharedPreferences? _prefs;

  Future<SharedPreferences> get _p async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  // Secure storage
  Future<void> saveSecure(String key, String value) =>
      _secure.write(key: key, value: value);

  Future<String?> getSecure(String key) => _secure.read(key: key);

  Future<void> deleteSecure(String key) => _secure.delete(key: key);

  Future<void> clearSecure() => _secure.deleteAll();

  // Shared preferences
  Future<void> setString(String key, String value) async =>
      (await _p).setString(key, value);

  Future<String?> getString(String key) async => (await _p).getString(key);

  Future<void> setBool(String key, bool value) async =>
      (await _p).setBool(key, value);

  Future<bool?> getBool(String key) async => (await _p).getBool(key);

  Future<void> remove(String key) async => (await _p).remove(key);

  Future<void> clear() async => (await _p).clear();
}
