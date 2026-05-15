import { get } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { TrendSignal } from '../../types/trend/trend_types';

export const trendsApi = {
  list: (params?: { category?: string; trajectory?: string; limit?: number }): Promise<APIResponse<TrendSignal[]>> =>
    get('/trends', params),

  getById: (id: string): Promise<APIResponse<TrendSignal>> =>
    get(`/trends/${id}`),

  radar: (params?: { location_id?: string }): Promise<APIResponse<unknown>> =>
    get('/agents/track4/trends/radar', params),

  forecast: (params?: { service_category?: string }): Promise<APIResponse<unknown>> =>
    get('/agents/track4/trends/forecast', params),
};
