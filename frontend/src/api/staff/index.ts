import { get } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { StaffProfile } from '../../types/staff/staff_types';

export const staffApi = {
  list: (params?: { location_id?: string; is_available?: boolean }): Promise<APIResponse<StaffProfile[]>> =>
    get('/staff', params),

  getById: (id: string): Promise<APIResponse<StaffProfile>> =>
    get(`/staff/${id}`),

  me: (): Promise<APIResponse<StaffProfile>> =>
    get('/staff/me'),

  performance: (staffId: string, params?: { period?: string }): Promise<APIResponse<unknown>> =>
    get(`/staff/${staffId}/performance`, params),

  attritionRisk: (): Promise<APIResponse<StaffProfile[]>> =>
    get('/agents/track2/attrition/at-risk'),
};
