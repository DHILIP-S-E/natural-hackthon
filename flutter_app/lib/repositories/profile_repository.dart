import 'dart:convert';
import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api/api_client.dart';
import '../core/api/endpoints.dart';
import '../core/firebase/firebase_storage_service.dart';
import '../models/face_analysis.dart';
import '../models/client_profile.dart';

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  final client = ref.watch(apiClientProvider);
  final storageService = ref.watch(firebaseStorageServiceProvider);
  return ProfileRepository(client, storageService);
});

class ProfileRepository {
  final ApiClient _client;
  final FirebaseStorageService _storageService;

  ProfileRepository(this._client, this._storageService);

  Future<FaceAnalysisResult> scanFace({
    required String customerId,
    required File imageFile,
  }) async {
    final photoUrl = await _storageService.uploadCustomerPhoto(
      customerId: customerId,
      imageFile: imageFile,
    );

    final bytes = await imageFile.readAsBytes();
    final base64Image = base64Encode(bytes);

    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.scanFace,
      data: {
        'customer_id': customerId,
        'photo_base64': base64Image,
        'photo_url': photoUrl,
      },
    );

    return FaceAnalysisResult.fromJson(response.data!);
  }

  Future<ClientProfile> saveProfile({
    required String customerId,
    required String analysisId,
    required ClientProfile profile,
  }) async {
    final response = await _client.post<Map<String, dynamic>>(
      Endpoints.saveProfile,
      data: {
        'customer_id': customerId,
        'analysis_id': analysisId,
        'edited_profile': profile.toJson(),
      },
    );

    return ClientProfile.fromJson(response.data!);
  }

  Future<ClientProfile?> getProfile(String customerId) async {
    try {
      final response = await _client.get<Map<String, dynamic>>(
        Endpoints.profile(customerId),
      );
      return ClientProfile.fromJson(response.data!);
    } catch (_) {
      return null;
    }
  }
}
