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
  created_at?: string;
}
