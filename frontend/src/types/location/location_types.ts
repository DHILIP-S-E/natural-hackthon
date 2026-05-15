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
