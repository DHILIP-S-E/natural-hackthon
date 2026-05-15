import { get } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { AnalyticsOverview } from '../../types/analytics/analytics_types';

export const analyticsApi = {
  overview: (params?: { location_id?: string; period?: string }): Promise<APIResponse<AnalyticsOverview>> =>
    get('/analytics/overview', params),

  revenue: (params?: { location_id?: string; period?: string }): Promise<APIResponse<unknown>> =>
    get('/analytics/revenue', params),

  soulskin: (params?: { location_id?: string }): Promise<APIResponse<unknown>> =>
    get('/analytics/soulskin', params),

  biDashboard: (params?: { location_id?: string }): Promise<APIResponse<unknown>> =>
    get('/analytics/bi-dashboard', params),

  franchise: (params?: { period?: string }): Promise<APIResponse<unknown>> =>
    get('/franchise-dashboard/overview', params),
};
