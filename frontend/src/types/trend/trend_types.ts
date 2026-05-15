export interface TrendSignal {
  id: string;
  trend_name: string;
  description: string;
  service_category: string;
  overall_signal_strength: number;
  trajectory: 'emerging' | 'growing' | 'peak' | 'declining';
  longevity_label: 'fad' | 'trend' | 'movement';
  celebrity_trigger?: string;
  climate_correlation?: unknown;
}
