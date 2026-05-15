class ClientProfile {
  final String profileId;
  final String customerId;
  final String faceAnalysisId;
  final String hairType;
  final String hairCondition;
  final List<String> hairConcerns;
  final String skinTone;
  final String skinCondition;
  final List<String> allergies;
  final bool profileComplete;
  final bool userEdited;

  const ClientProfile({
    this.profileId = '',
    required this.customerId,
    this.faceAnalysisId = '',
    required this.hairType,
    required this.hairCondition,
    required this.hairConcerns,
    required this.skinTone,
    required this.skinCondition,
    required this.allergies,
    this.profileComplete = false,
    this.userEdited = false,
  });

  factory ClientProfile.fromJson(Map<String, dynamic> json) => ClientProfile(
        profileId: json['profile_id'] as String? ?? '',
        customerId: json['customer_id'] as String? ?? '',
        faceAnalysisId: json['face_analysis_id'] as String? ?? '',
        hairType: json['hair_type'] as String? ?? '',
        hairCondition: json['hair_condition'] as String? ?? '',
        hairConcerns: List<String>.from(json['hair_concerns'] as List? ?? []),
        skinTone: json['skin_tone'] as String? ?? '',
        skinCondition: json['skin_condition'] as String? ?? '',
        allergies: List<String>.from(json['allergies'] as List? ?? []),
        profileComplete: json['profile_complete'] as bool? ?? false,
        userEdited: json['user_edited'] as bool? ?? false,
      );

  Map<String, dynamic> toJson() => {
        'customer_id': customerId,
        'face_analysis_id': faceAnalysisId,
        'hair_type': hairType,
        'hair_condition': hairCondition,
        'hair_concerns': hairConcerns,
        'skin_tone': skinTone,
        'skin_condition': skinCondition,
        'allergies': allergies,
      };

  ClientProfile copyWith({
    String? profileId,
    String? customerId,
    String? faceAnalysisId,
    String? hairType,
    String? hairCondition,
    List<String>? hairConcerns,
    String? skinTone,
    String? skinCondition,
    List<String>? allergies,
    bool? profileComplete,
    bool? userEdited,
  }) =>
      ClientProfile(
        profileId: profileId ?? this.profileId,
        customerId: customerId ?? this.customerId,
        faceAnalysisId: faceAnalysisId ?? this.faceAnalysisId,
        hairType: hairType ?? this.hairType,
        hairCondition: hairCondition ?? this.hairCondition,
        hairConcerns: hairConcerns ?? this.hairConcerns,
        skinTone: skinTone ?? this.skinTone,
        skinCondition: skinCondition ?? this.skinCondition,
        allergies: allergies ?? this.allergies,
        profileComplete: profileComplete ?? this.profileComplete,
        userEdited: userEdited ?? this.userEdited,
      );
}
