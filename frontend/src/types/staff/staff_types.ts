export interface StaffProfile {
  id: string;
  user_id: string;
  employee_id: string;
  name: string;
  email: string;
  designation: string;
  location_id: string;
  skill_level: 'L1' | 'L2' | 'L3';
  specializations: string[];
  is_available: boolean;
  current_rating: number;
  total_services_done: number;
  soulskin_certified: boolean;
  attrition_risk_label: 'low' | 'medium' | 'high';
}
