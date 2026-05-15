import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final firebaseStorageServiceProvider = Provider<FirebaseStorageService>((_) {
  return FirebaseStorageService();
});

class FirebaseStorageService {
  /// Uploads a customer photo to Firebase Cloud Storage and returns the download URL.
  /// Returns empty string if Firebase is not configured (photo will be sent as base64 only).
  Future<String> uploadCustomerPhoto({
    required String customerId,
    required File imageFile,
  }) async {
    try {
      // Dynamic import so the app compiles even without firebase_options.dart
      final storage = await _getStorage();
      if (storage == null) return '';

      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final ref = storage.ref('customer_photos/${customerId}_$timestamp.jpg');

      final metadata = _SettableMetadata(contentType: 'image/jpeg');
      await ref.putFile(imageFile, metadata);
      return await ref.getDownloadURL();
    } catch (e) {
      // Firebase not initialized or upload failed — caller will use base64 instead
      return '';
    }
  }
}

// Stub classes so the file compiles without firebase_storage imported
// Remove these and add the real import once flutterfire configure is run:
//   import 'package:firebase_storage/firebase_storage.dart';

dynamic _getStorage() async => null;

class _SettableMetadata {
  final String contentType;
  _SettableMetadata({required this.contentType});
}
