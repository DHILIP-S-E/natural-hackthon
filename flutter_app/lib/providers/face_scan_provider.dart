import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/face_analysis.dart';
import '../models/client_profile.dart';

class FaceScanState {
  final File? imageFile;
  final String? imageUrl;
  final FaceAnalysisResult? analysisResult;
  final ClientProfile? editedProfile;
  final bool isUploading;
  final bool isAnalyzing;
  final String? error;

  const FaceScanState({
    this.imageFile,
    this.imageUrl,
    this.analysisResult,
    this.editedProfile,
    this.isUploading = false,
    this.isAnalyzing = false,
    this.error,
  });

  bool get hasImage => imageFile != null;
  bool get hasAnalysis => analysisResult != null;
  bool get isBusy => isUploading || isAnalyzing;

  FaceScanState copyWith({
    File? imageFile,
    String? imageUrl,
    FaceAnalysisResult? analysisResult,
    ClientProfile? editedProfile,
    bool? isUploading,
    bool? isAnalyzing,
    String? error,
  }) =>
      FaceScanState(
        imageFile: imageFile ?? this.imageFile,
        imageUrl: imageUrl ?? this.imageUrl,
        analysisResult: analysisResult ?? this.analysisResult,
        editedProfile: editedProfile ?? this.editedProfile,
        isUploading: isUploading ?? this.isUploading,
        isAnalyzing: isAnalyzing ?? this.isAnalyzing,
        error: error,
      );

  FaceScanState clearError() => FaceScanState(
        imageFile: imageFile,
        imageUrl: imageUrl,
        analysisResult: analysisResult,
        editedProfile: editedProfile,
        isUploading: isUploading,
        isAnalyzing: isAnalyzing,
      );
}

class FaceScanNotifier extends StateNotifier<FaceScanState> {
  FaceScanNotifier() : super(const FaceScanState());

  void setImage(File file) {
    state = state.copyWith(imageFile: file);
  }

  void setUploading(bool value) {
    state = state.copyWith(isUploading: value);
  }

  void setAnalyzing(bool value) {
    state = state.copyWith(isAnalyzing: value);
  }

  void setAnalysisResult(FaceAnalysisResult result) {
    final profile = ClientProfile(
      customerId: result.customerId,
      faceAnalysisId: result.analysisId,
      hairType: result.hair.type,
      hairCondition: result.hair.condition,
      hairConcerns: List.from(result.hair.concerns),
      skinTone: result.skin.tone,
      skinCondition: result.skin.condition,
      allergies: [],
    );
    state = state.copyWith(
      analysisResult: result,
      editedProfile: profile,
      imageUrl: result.photoUrl,
    );
  }

  void updateHairType(String value) {
    if (state.editedProfile == null) return;
    state = state.copyWith(
      editedProfile: state.editedProfile!.copyWith(hairType: value),
    );
  }

  void updateHairCondition(String value) {
    if (state.editedProfile == null) return;
    state = state.copyWith(
      editedProfile: state.editedProfile!.copyWith(hairCondition: value),
    );
  }

  void toggleHairConcern(String concern) {
    if (state.editedProfile == null) return;
    final concerns = List<String>.from(state.editedProfile!.hairConcerns);
    if (concerns.contains(concern)) {
      concerns.remove(concern);
    } else {
      concerns.add(concern);
    }
    state = state.copyWith(
      editedProfile: state.editedProfile!.copyWith(hairConcerns: concerns),
    );
  }

  void updateSkinTone(String value) {
    if (state.editedProfile == null) return;
    state = state.copyWith(
      editedProfile: state.editedProfile!.copyWith(skinTone: value),
    );
  }

  void updateSkinCondition(String value) {
    if (state.editedProfile == null) return;
    state = state.copyWith(
      editedProfile: state.editedProfile!.copyWith(skinCondition: value),
    );
  }

  void updateAllergies(List<String> allergies) {
    if (state.editedProfile == null) return;
    state = state.copyWith(
      editedProfile: state.editedProfile!.copyWith(allergies: allergies),
    );
  }

  void setError(String? error) {
    state = state.copyWith(error: error);
  }

  void reset() {
    state = const FaceScanState();
  }
}

final faceScanProvider =
    StateNotifierProvider<FaceScanNotifier, FaceScanState>(
  (_) => FaceScanNotifier(),
);
