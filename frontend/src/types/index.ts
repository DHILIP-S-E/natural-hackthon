/* AURA TypeScript types */

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  avatar_url?: string;
  phone?: string;
  preferred_language?: string;
}

export type UserRole = 'super_admin' | 'regional_manager' | 'franchise_owner' | 'salon_manager' | 'stylist' | 'customer';

export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
  errors: string[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Location {
  id: string;
  name: string;
  code: string;
  city: string;
  state: string;
  address: string;
  phone?: string;
  seating_capacity?: number;
  is_active: boolean;
  smart_mirror_enabled: boolean;
  soulskin_enabled: boolean;
  operating_hours?: Record<string, { open: string; close: string }>;
  monthly_revenue_target?: number;
  latitude?: number;
  longitude?: number;
}

export interface StaffProfile {
  id: string;
  user_id: string;
  employee_id: string;
  name: string;
  email: string;
  designation: string;
  skill_level: 'L1' | 'L2' | 'L3';
  specializations: string[];
  is_available: boolean;
  current_rating: number;
  total_services_done: number;
  soulskin_certified: boolean;
  attrition_risk_label: 'low' | 'medium' | 'high';
}

export interface CustomerProfile {
  id: string;
  user_id: string;
  name: string;
  beauty_score: number;
  passport_completeness: number;
  // Hair
  hair_type: string; hair_texture: string; hair_porosity: string; hair_density: string;
  scalp_condition: string; hair_damage_level: number;
  natural_hair_color: string; current_hair_color: string;
  // Skin
  skin_type: string; skin_tone: string; undertone: string;
  primary_skin_concerns: string[]; skin_sensitivity: string;
  acne_severity: number; pigmentation_level: number;
  // SOULSKIN
  dominant_archetype: Archetype | null;
  archetype_history: { archetype: string; date: string }[];
  emotional_sensitivity: string;
  // Lifestyle
  city: string; climate_type: string;
  local_uv_index: number; local_humidity: number; local_aqi: number;
  stress_level: string; diet_type: string;
  // Safety
  known_allergies: string[];
  // Goals
  primary_goal: string; goal_progress_pct: number;
  total_visits: number; lifetime_value: number;
}

export type Archetype = 'phoenix' | 'river' | 'moon' | 'bloom' | 'storm';

export interface ArchetypeInfo {
  name: string;
  emoji: string;
  color: string;
  element: string;
  description: string;
}

export const ARCHETYPES: Record<Archetype, ArchetypeInfo> = {
  phoenix: { name: 'Phoenix', emoji: '🔥', color: '#E8611A', element: 'Fire', description: 'You are standing at the edge of something ending. You are not afraid of the fire.' },
  river: { name: 'River', emoji: '🌊', color: '#4A9FD4', element: 'Water', description: 'You are in flow. Something is shifting inside you.' },
  moon: { name: 'Moon', emoji: '🌙', color: '#7B68C8', element: 'Light', description: 'You are in a quiet phase. You need softness and gentle reflection.' },
  bloom: { name: 'Bloom', emoji: '🌸', color: '#E8A87C', element: 'Earth', description: 'You are growing. Something new is opening inside you.' },
  storm: { name: 'Storm', emoji: '⛈️', color: '#6B8FA6', element: 'Air', description: 'You carry weight today. You need grounding, not stimulation.' },
};

export interface Service {
  id: string;
  name: string;
  category: string;
  subcategory?: string;
  short_description: string;
  duration_minutes: number;
  base_price: number;
  skill_required: string;
  is_chemical: boolean;
  ar_preview_available: boolean;
  tags: string[];
  image_url?: string;
}

export interface Booking {
  id: string;
  booking_number: string;
  customer_id: string;
  location_id: string;
  stylist_id: string;
  service_id: string;
  status: BookingStatus;
  scheduled_at: string;
  base_price: number;
  final_price: number;
  payment_status: string;
  source: string;
  soulskin_session_id?: string;
}

export type BookingStatus = 'pending' | 'confirmed' | 'checked_in' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';

export interface SoulskinSession {
  id: string;
  booking_id?: string;
  customer_id: string;
  question_1_song?: string;
  question_2_colour?: string;
  question_3_word?: string;
  archetype?: Archetype;
  soul_reading?: string;
  archetype_reason?: string;
  service_protocol?: Record<string, string>;
  colour_direction?: Record<string, string>;
  sensory_environment?: any;
  touch_protocol?: any;
  custom_formula?: any;
  stylist_script?: Record<string, string>;
  mirror_monologue?: string;
  private_life_note?: string;
  look_created?: string;
  session_completed: boolean;
}

export interface TrendSignal {
  id: string;
  trend_name: string;
  description: string;
  service_category: string;
  overall_signal_strength: number;
  trajectory: 'emerging' | 'growing' | 'peak' | 'declining';
  longevity_label: 'fad' | 'trend' | 'movement';
  celebrity_trigger?: string;
  climate_correlation?: any;
}

export interface ClimateRecommendation {
  city: string;
  temperature_celsius: number;
  humidity_pct: number;
  uv_index: number;
  aqi: number;
  weather_condition: string;
  hair_recommendations: { alerts: string[]; home_care_tip: string };
  skin_recommendations: { alerts: string[]; home_care_tip: string };
  is_alert: boolean;
}

export interface AnalyticsOverview {
  total_bookings: number;
  completed_bookings: number;
  total_revenue: number;
  avg_quality_score: number;
  soulskin_sessions: number;
  total_customers: number;
  avg_customer_rating: number;
}

export interface QueueEntry {
  id: string;
  customer_name: string;
  customer_phone?: string;
  customer_id?: string;
  service_id?: string;
  preferred_stylist_id?: string;
  position_in_queue: number;
  status: 'waiting' | 'assigned' | 'in_service' | 'completed' | 'left';
  estimated_wait_mins: number;
  walk_in_source?: string;
  joined_queue_at?: string;
  notes?: string;
}

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

export interface TrainingRecord {
  id: string;
  staff_id: string;
  training_name: string;
  training_type: string;
  service_category?: string;
  provider?: string;
  hours_completed: number;
  cost_to_company: number;
  passed: boolean;
  score?: number;
  includes_soulskin: boolean;
}

export interface Notification {
  id: string;
  title?: string;
  body?: string;
  notification_type?: string;
  channel?: string;
  priority?: string;
  is_read: boolean;
  data?: any;
  created_at?: string;
}

export interface HomecarePlan {
  id: string;
  customer_id: string;
  soulskin_archetype?: string;
  plan_duration_weeks?: number;
  hair_routine?: any;
  skin_routine?: any;
  climate_adjustments?: any;
  archetype_rituals?: any;
  product_recommendations?: any;
  dos?: string[];
  donts?: string[];
  next_visit_recommendation?: string;
  whatsapp_sent: boolean;
  generated_at?: string;
}

export interface BeautyJourneyPlan {
  id: string;
  customer_id: string;
  plan_duration_weeks?: number;
  primary_goal?: string;
  milestones?: any[];
  expected_outcomes?: Record<string, string>;
  estimated_total_cost?: number;
  ai_notes?: string;
  whatsapp_sent: boolean;
  generated_at?: string;
}

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

export interface DigitalTwin {
  id: string;
  customer_id: string;
  model_data_url?: string;
  texture_url?: string;
  skin_timeline?: any[];
  future_simulations?: any[];
  hairstyle_tryons?: any[];
  consent_given: boolean;
  is_active: boolean;
}

export interface ServiceSession {
  id: string;
  booking_id: string;
  sop_id?: string;
  status: 'not_started' | 'active' | 'paused' | 'completed' | 'abandoned';
  current_step: number;
  steps_total?: number;
  steps_completed?: number[];
  started_at?: string;
  completed_at?: string;
  soulskin_active: boolean;
  archetype_applied?: string;
  quality_score?: number;
  sop_compliance_pct?: number;
  deviations?: any[];
  ai_coaching_prompts?: any;
  stylist_notes?: string;
  has_offline_changes: boolean;
}
