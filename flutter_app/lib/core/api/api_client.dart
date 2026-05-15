import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/env.dart';
import '../../config/constants.dart';
import '../storage/local_storage.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(localStorageProvider);
  return ApiClient(storage);
});

class ApiClient {
  final LocalStorage _storage;
  late final Dio _dio;

  ApiClient(this._storage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: Env.baseUrl,
        connectTimeout: AppConstants.connectTimeout,
        receiveTimeout: AppConstants.receiveTimeout,
        headers: {'Content-Type': 'application/json'},
      ),
    );
    _dio.interceptors.addAll([_authInterceptor(), _errorInterceptor()]);
  }

  InterceptorsWrapper _authInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.getSecure(AppConstants.tokenKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    );
  }

  InterceptorsWrapper _errorInterceptor() {
    return InterceptorsWrapper(
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _tryRefresh();
          if (refreshed) {
            final retryRequest = await _dio.fetch(error.requestOptions);
            return handler.resolve(retryRequest);
          }
          await _storage.deleteSecure(AppConstants.tokenKey);
          await _storage.deleteSecure(AppConstants.refreshTokenKey);
        }
        handler.next(error);
      },
    );
  }

  Future<bool> _tryRefresh() async {
    try {
      final refreshToken =
          await _storage.getSecure(AppConstants.refreshTokenKey);
      if (refreshToken == null) return false;
      final response = await _dio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      final newToken = response.data['token'] as String?;
      if (newToken == null) return false;
      await _storage.saveSecure(AppConstants.tokenKey, newToken);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) => _dio.get(path, queryParameters: queryParameters);

  Future<Response<T>> post<T>(String path, {dynamic data}) =>
      _dio.post(path, data: data);

  Future<Response<T>> put<T>(String path, {dynamic data}) =>
      _dio.put(path, data: data);

  Future<Response<T>> delete<T>(String path) => _dio.delete(path);

  Future<Response<T>> patch<T>(String path, {dynamic data}) =>
      _dio.patch(path, data: data);
}
