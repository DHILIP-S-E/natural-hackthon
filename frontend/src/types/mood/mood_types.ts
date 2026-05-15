export interface MoodDetection {
  id: string;
  customer_id: string;
  detected_emotion: string;
  emotion_confidence: number;
  energy_level?: string;
  recommended_archetype?: string;
  service_adjustment?: string;
  captured_at?: string;
}
