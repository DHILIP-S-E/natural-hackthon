import { get, post } from '../base/api_base';
import type { APIResponse } from '../base/base_type';

export interface LoyaltyProfile {
  customer_id: string;
  tier: string;
  total_points: number;
  lifetime_value: number;
  referral_code: string;
  visits_count: number;
  last_visit_date?: string;
}

export interface LoyaltyTransaction {
  id: string; type: string; points: number; description: string; created_at: string;
}

export const loyaltyApi = {
  me: (): Promise<APIResponse<LoyaltyProfile>> =>
    get('/loyalty/me'),

  transactions: (params?: { limit?: number }): Promise<APIResponse<LoyaltyTransaction[]>> =>
    get('/loyalty/transactions', params),

  redeem: (points: number): Promise<APIResponse<{ success: boolean; discount_amount: number }>> =>
    post('/loyalty/redeem', { points }),
};
