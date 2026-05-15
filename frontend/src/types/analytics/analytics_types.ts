export interface AnalyticsOverview {
  total_bookings: number;
  completed_bookings: number;
  total_revenue: number;
  avg_quality_score: number;
  soulskin_sessions: number;
  total_customers: number;
  avg_customer_rating: number;
}

export interface RevenueData {
  period: string;
  revenue: number;
  target: number;
  growth_pct: number;
}
