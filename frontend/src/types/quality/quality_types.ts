export interface QualityAssessment {
  id: string;
  booking_id: string;
  stylist_id: string;
  location_id: string;
  service_id: string;
  sop_compliance_score: number;
  timing_score: number;
  customer_rating?: number;
  manager_rating?: number;
  overall_score: number;
  is_flagged: boolean;
  flag_reason?: string;
  soulskin_alignment_score?: number;
  ai_feedback?: string;
  reviewed_by_manager: boolean;
  created_at?: string;
}
