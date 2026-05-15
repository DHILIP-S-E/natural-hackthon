class HairAnalysis {
  final String type;
  final String color;
  final String condition;
  final List<String> concerns;
  final String scalp;

  const HairAnalysis({
    required this.type,
    required this.color,
    required this.condition,
    required this.concerns,
    required this.scalp,
  });

  factory HairAnalysis.fromJson(Map<String, dynamic> json) => HairAnalysis(
        type: json['type'] as String? ?? '',
        color: json['color'] as String? ?? '',
        condition: json['condition'] as String? ?? '',
        concerns: List<String>.from(json['concerns'] as List? ?? []),
        scalp: json['scalp'] as String? ?? '',
      );

  Map<String, dynamic> toJson() => {
        'type': type,
        'color': color,
        'condition': condition,
        'concerns': concerns,
        'scalp': scalp,
      };

  HairAnalysis copyWith({
    String? type,
    String? color,
    String? condition,
    List<String>? concerns,
    String? scalp,
  }) =>
      HairAnalysis(
        type: type ?? this.type,
        color: color ?? this.color,
        condition: condition ?? this.condition,
        concerns: concerns ?? this.concerns,
        scalp: scalp ?? this.scalp,
      );
}

class SkinAnalysis {
  final String tone;
  final String condition;
  final List<String> issues;

  const SkinAnalysis({
    required this.tone,
    required this.condition,
    required this.issues,
  });

  factory SkinAnalysis.fromJson(Map<String, dynamic> json) => SkinAnalysis(
        tone: json['tone'] as String? ?? '',
        condition: json['condition'] as String? ?? '',
        issues: List<String>.from(json['issues'] as List? ?? []),
      );

  Map<String, dynamic> toJson() => {
        'tone': tone,
        'condition': condition,
        'issues': issues,
      };

  SkinAnalysis copyWith({
    String? tone,
    String? condition,
    List<String>? issues,
  }) =>
      SkinAnalysis(
        tone: tone ?? this.tone,
        condition: condition ?? this.condition,
        issues: issues ?? this.issues,
      );
}

class FaceAnalysisResult {
  final String analysisId;
  final String customerId;
  final String photoUrl;
  final HairAnalysis hair;
  final SkinAnalysis skin;
  final double confidence;

  const FaceAnalysisResult({
    required this.analysisId,
    required this.customerId,
    required this.photoUrl,
    required this.hair,
    required this.skin,
    required this.confidence,
  });

  factory FaceAnalysisResult.fromJson(Map<String, dynamic> json) {
    final analysis = json['analysis'] as Map<String, dynamic>? ?? json;
    return FaceAnalysisResult(
      analysisId: json['analysis_id'] as String? ?? '',
      customerId: json['customer_id'] as String? ?? '',
      photoUrl: json['photo_url'] as String? ?? '',
      hair: HairAnalysis.fromJson(analysis['hair'] as Map<String, dynamic>? ?? {}),
      skin: SkinAnalysis.fromJson(analysis['skin'] as Map<String, dynamic>? ?? {}),
      confidence: (analysis['overall_confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
