import type { Archetype } from '../soulskin/soulskin_types';

export interface CustomerProfile {
  id: string;
  user_id: string;
  name: string;
  beauty_score: number;
  passport_completeness: number;
  hair_type: string; hair_texture: string; hair_porosity: string; hair_density: string;
  scalp_condition: string; hair_damage_level: number;
  natural_hair_color: string; current_hair_color: string;
  skin_type: string; skin_tone: string; undertone: string;
  primary_skin_concerns: string[]; skin_sensitivity: string;
  acne_severity: number; pigmentation_level: number;
  dominant_archetype: Archetype | null;
  archetype_history: { archetype: string; date: string }[];
  emotional_sensitivity: string;
  city: string; climate_type: string;
  local_uv_index: number; local_humidity: number; local_aqi: number;
  stress_level: string; diet_type: string;
  known_allergies: string[];
  primary_goal: string; goal_progress_pct: number;
  total_visits: number; lifetime_value: number;
}
