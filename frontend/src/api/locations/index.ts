import { get } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { Location } from '../../types/location/location_types';

export const locationsApi = {
  list: (params?: { is_active?: boolean }): Promise<APIResponse<Location[]>> =>
    get('/locations', params),

  getById: (id: string): Promise<APIResponse<Location>> =>
    get(`/locations/${id}`),

  nearby: (params: { lat: number; lng: number; radius_km?: number }): Promise<APIResponse<Location[]>> =>
    get('/locations/nearby', params),

  analytics: (id: string, period?: string): Promise<APIResponse<unknown>> =>
    get(`/locations/${id}/analytics`, { period }),
};
