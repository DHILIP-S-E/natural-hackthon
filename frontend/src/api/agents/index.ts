import { get, post } from '../base/api_base';
import type { APIResponse } from '../base/base_type';

export const agentsApi = {
  // Track 1 — Standardization
  qualityScore: (bookingId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track1/quality/score', { booking_id: bookingId }),

  sopCompliance: (sessionId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track1/sop/compliance', { session_id: sessionId }),

  // Track 2 — Staff Intelligence
  attritionRisk: (): Promise<APIResponse<unknown>> =>
    get('/agents/track2/attrition/at-risk'),

  trainingGaps: (staffId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track2/training/gaps', { staff_id: staffId }),

  // Track 3 — Personalization
  passport: (customerId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track3/passport/full', { customer_id: customerId }),

  nextBest: (customerId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track3/recommendations/next-best', { customer_id: customerId }),

  // Track 4 — Trend Intelligence
  trendRadar: (locationId?: string): Promise<APIResponse<unknown>> =>
    get('/agents/track4/trends/radar', { location_id: locationId }),

  // Track 5 — Experience
  waitOptimize: (locationId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track5/wait/optimize', { location_id: locationId }),

  chatbot: (data: { message: string; customer_id?: string; session_id?: string }): Promise<APIResponse<{ reply: string }>> =>
    post('/chatbot/message', data),

  // Track 6 — Intelligence & BI
  forecast: (params?: { location_id?: string; days?: number }): Promise<APIResponse<unknown>> =>
    get('/agents/track6/forecast', params),
};
