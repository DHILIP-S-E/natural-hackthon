import { get, post, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { QualityAssessment } from '../../types/quality/quality_types';

export const qualityApi = {
  list: (params?: { location_id?: string; stylist_id?: string; limit?: number }): Promise<APIResponse<QualityAssessment[]>> =>
    get('/quality', params),

  getById: (id: string): Promise<APIResponse<QualityAssessment>> =>
    get(`/quality/${id}`),

  create: (data: Partial<QualityAssessment>): Promise<APIResponse<QualityAssessment>> =>
    post('/quality', data),

  review: (id: string, data: { manager_rating: number; notes?: string }): Promise<APIResponse<QualityAssessment>> =>
    put(`/quality/${id}/review`, data),

  stylistScores: (staffId: string): Promise<APIResponse<unknown>> =>
    get(`/agents/track1/quality/stylist-scores`, { staff_id: staffId }),
};
